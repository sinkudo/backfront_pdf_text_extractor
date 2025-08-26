import ast
import os
import re
import subprocess
import tempfile
from itertools import zip_longest
from pathlib import Path, PurePath
from sys import platform
from typing import Dict, Iterable, List, Optional, Union
from pdfminer.cmapdb import CMapDB

from pypdf import PdfWriter as pypdfwriter

import fitz
from fontTools.ttLib import TTFont
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTChar, LTTextLineHorizontal
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdftypes import resolve1
from pdfminer.psparser import PSLiteral

from pdf_broken_encoding_reader import config
from pdf_broken_encoding_reader import functions
from pdf_broken_encoding_reader.functions import correctly_resize, junk_string
from pdf_broken_encoding_reader.model import Model
from pdf_broken_encoding_reader.pdf_worker import pdf_text_correcter
from pdf_broken_encoding_reader.pdf_worker.pdf_text_correcter import correct_string_incorrect_chars


class PDFReader:
    def __init__(self) -> None:
        self.extract_path = config.folders.get("extracted_data_folder")
        self.model = Model()
        self.text = None
        self.match_dict = {}
        self.__cached_fonts = None
        self.__fontname2basefont = {}
        self.__unicodemaps = {}
        self.__name2code = {}
        self.__fonts_path = config.folders.get("extracted_fonts_folder")
        self.__glyphs_path = config.folders.get("extracted_glyphs_folder")
        self.__need2correct = True
        self.__pdf_fonts_dict = {}
        self.__glyph_to_unicode = {}

    def restore_text(self, pdf_path: Path, start_page: int = 0, end_page: int = 0) -> str:
        assert end_page > start_page or start_page == end_page == 0, "wrong pages range"
        self.text = ""
        self.match_dict = {}
        self.__read_pdf(pdf_path)
        self.__match_glyphs_and_encoding_for_all()
        text = self.__restore_text(pdf_path, start=start_page, end=end_page)
        if self.__need2correct:
            text = pdf_text_correcter.correct_collapsed_text(text)
        return text

    def __read_pdf(self, pdf_path: Path, fonts_path: Path, glyphs_path: Path) -> None:
        self.__extract_fonts(pdf_path, fonts_path)
        self.__extract_glyphs(fonts_path, glyphs_path)

    def __extract_fonts(self, pdf_path: Path, fonts_path: Path) -> None:
        doc = fitz.open(pdf_path)
        xref_visited = []

        junk = 0
        for page_num in range(doc.page_count):
            page = doc.get_page_fonts(page_num)
            for fontinfo in page:
                junk += 1
                xref = fontinfo[0]
                if xref in xref_visited:
                    continue
                xref_visited.append(xref)
                font = doc.extract_font(xref, named=True)
                if font["ext"] != "n/a":
                    font_path = fonts_path.joinpath(f"{font['name']}{junk_string}{str(junk)}.{font['ext']}")
                    ofile = open(font_path, "wb")
                    ofile.write(font["content"])
                    ofile.close()

                    self.__pdf_fonts_dict[font['name']] = {"xref": xref, "font_data": font}
        doc.close()

    def __extract_glyphs(self, fonts_path: Path, glyphs_path: Path) -> None:
        font_files = list(fonts_path.iterdir())
        white_spaces = {}
        for font_file in font_files:
            font_white_spaces = {}
            font_name = Path(font_file).parts[-1].split(".")[0]
            font_name = re.split(junk_string, font_name)[0]
            save_path = glyphs_path.joinpath(font_name)
            font_path = fonts_path.joinpath(os.fsdecode(font_file))

            save_path.mkdir()
            save_path = str(save_path)
            font_path = str(font_path)
            ff_path = config.folders.get("ffwraper_folder")

            devnull = open(os.devnull, "wb")
            if platform == "linux" or platform == "linux2":
                result = subprocess.check_output(f"fontforge -script {str(ff_path)} generate_all_images {save_path} {font_path}", shell=True, stderr=devnull)
            else:
                console_command = f"ffpython {str(ff_path)} generate_all_images {save_path} {font_path}"
                try:
                    result = subprocess.check_output(console_command, stderr=devnull)
                except Exception:
                    if font_file.suffix.lower() not in [".ttf", ".otf"]:
                        continue
                    font = TTFont(font_path)
                    name_table = font["name"]
                    for record in name_table.names:
                        record.string = "undef".encode("utf-16-be")
                    font.save(font_path)

                    result = subprocess.check_output(console_command, stderr=devnull)
            devnull.close()
            result = result.decode("utf-8")
            eval_list = list(ast.literal_eval(result))
            imgs_to_resize_set = set(eval_list[0])
            empty_glyphs = eval_list[1]
            names = eval_list[2]
            codes = eval_list[3]
            name2code = dict(zip_longest(names, codes))

            if font_name not in self.__name2code:
                self.__name2code[font_name] = name2code
            else:
                self.__name2code[font_name].update(name2code)

            for img in imgs_to_resize_set:
                if functions.is_empty(img) and "png" in img:
                    uni_whitespace = (PurePath(img).parts[-1]).split(".")[0]
                    name_whitespace = ""
                    try:
                        name_whitespace = chr(int(uni_whitespace))
                    except Exception:
                        name_whitespace = uni_whitespace
                    finally:
                        font_white_spaces[name_whitespace] = " "
                        os.remove(img)
                else:
                    correctly_resize(img)
            white_spaces[font_name] = empty_glyphs
        self.white_spaces = white_spaces

    def __match_glyphs_and_encoding_for_all(self, fonts_path: Path, glyphs_path: Path) -> None:
        fonts = fonts_path.iterdir()
        dicts = self.white_spaces
        for font_file in fonts:
            fontname_with_ext = PurePath(font_file).parts[-1]
            fontname = fontname_with_ext.split(".")[0]
            fontname = fontname.split(junk_string)[0]
            matching_res = self.__match_glyphs_and_encoding(glyphs_path.joinpath(fontname))
            if fontname in dicts:
                dicts[fontname].update(matching_res)
            else:
                dicts[fontname] = matching_res
        self.match_dict = dicts

    def __match_glyphs_and_encoding(self, images_path: Path) -> Dict[Union[str, int], str]:
        images = images_path.glob("*")
        dictionary = {}
        alphas = {}
        image_paths = [img for img in images]
        batch_size = 32
        num_batches = len(image_paths) // batch_size + (1 if len(image_paths) % batch_size != 0 else 0)
        for batch_idx in range(num_batches):
            batch_images = image_paths[batch_idx * batch_size:(batch_idx + 1) * batch_size]
            predictions = self.model.recognize_glyph(batch_images)
            for img, pred in zip(batch_images, predictions):
                key = img.parts[-1].split(".")
                key = "".join(key[:-1])
                char = chr(int(pred))
                try:
                    dictionary[chr(int(key))] = chr(int(pred))
                    k = chr(int(key))
                except Exception:
                    dictionary[key] = chr(int(pred))
                    k = key
                if char.isalpha():
                    alphas.setdefault(char.lower(), []).append((img, k))

        return dictionary

    def __restore_text(self, pdf_path: Path, start: int = 0, end: int = 0) -> str:
        self.__cached_fonts = None
        self.__fontname2basefont = {}
        self.__unicodemaps = {}
        with open(pdf_path, "rb") as fp:
            parser = PDFParser(fp)
            document = PDFDocument(parser)
            pages_count = resolve1(document.catalog["Pages"])["Count"]
            end = pages_count if end == 0 else end

            rsrcmgr = PDFResourceManager()
            laparams = LAParams()

            # Create a PDF device object
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            full_text = ""
            # Iterate through each page of the PDF
            for page_num, page in enumerate(PDFPage.create_pages(document)):
                if page_num < start:
                    continue
                elif page_num >= end:
                    break
                interpreter.process_page(page)
                layout = device.get_result()
                cached_fonts = {}
                fonts = page.resources.get("Font")

                if not isinstance(fonts, dict):
                    Exception("fonts should be dictionary")
                for _, font_obj in fonts.items():
                    font_dict = resolve1(font_obj)
                    encoding = resolve1(font_dict.get("Encoding"))
                    f = rsrcmgr.get_font(objid=font_obj.objid, spec={"name": resolve1(font_obj)["BaseFont"].name})
                    self.__fontname2basefont[f.fontname] = f.basefont if hasattr(f, "basefont") else f.fontname

                    if hasattr(f, "unicode_map") and hasattr(f.unicode_map, "cid2unichr"):
                        basefont_else_fontname = self.__fontname2basefont[f.fontname]
                        self.__unicodemaps[basefont_else_fontname] = f.unicode_map.cid2unichr
                    if not (isinstance(encoding, dict) and ("/Differences" in encoding or "Differences" in encoding)):
                        cached_fonts[f.fontname] = []
                        continue
                    char_set_arr = [q.name if isinstance(q, PSLiteral) else "" for q in encoding["Differences"]]
                    cached_fonts[f.fontname] = char_set_arr

                self.__cached_fonts = rsrcmgr._cached_fonts
                page_text = []

                self.__extract_text_str(layout, cached_fonts, page_text)
                full_text += "".join(page_text)

        self.text = functions.remove_hyphenations(self.text)

        self.text = re.sub(r"\s+", " ", self.text)

        return full_text

    def __extract_text_str(self, o: Union[LTChar, LTTextLineHorizontal, Iterable], cached_fonts: dict, page_text: list) -> None:
        if isinstance(o, LTChar):
            self.process_char(o, cached_fonts)
        elif isinstance(o, LTTextLineHorizontal):
            self.process_text_line(o, page_text)
        elif isinstance(o, Iterable):
            self.process_iterable(o, cached_fonts, page_text)

    def process_iterable(self, iterable_obj: Iterable, cached_fonts: dict, page_text: list) -> None:
        for item in iterable_obj:
            self.__extract_text_str(item, cached_fonts, page_text)

    def process_text_line(self, text_line: LTTextLineHorizontal, page_text: list) -> None:
        # LTTextLineHorizontal
        text = text_line.get_text()
        text = text.replace("\n", " ").replace("\r", "").replace("\t", " ")
        page_text.append(text)

    def process_char(self, char_obj: LTChar, cached_fonts: dict) -> None:
        # LTChar
        char = char_obj.get_text()
        match_dict_key = char_obj.fontname

        if not cached_fonts.get(char_obj.fontname):
            try:
                char_obj._text = self.match_dict[match_dict_key][char]
            except Exception:
                char_obj._text = char
            return

        index = -1
        if "cid" in char:
            index = int(char[1:-1].split(":")[-1])
        elif "glyph" in char:
            glyph_unicode = int(char[5:])
            index = ord(self.__unicodemaps[glyph_unicode])
        else:
            try:
                index = ord(char)
                if ord(char) > len(cached_fonts[char_obj.fontname]) and char == "’":
                    char = "'"
                    index = ord(char)
                elif ord(char) > len(cached_fonts[char_obj.fontname]):
                    char_obj._text = self.match_dict[match_dict_key][char]
                    return
            except Exception:
                char_obj._text = char
                return

        try:
            glyph_name = cached_fonts[char_obj.fontname][index]
            char_obj._text = self.match_dict[match_dict_key][glyph_name]
        except Exception:
            char_obj._text = char

    def __correct_pages_text(self, o: Union[LTChar, LTTextLineHorizontal, Iterable], cached_fonts: dict, fulltext: list) -> None:
        if isinstance(o, LTChar):
            if o.get_text() == "’":
                o._text = "'"
            self.__correct_char_text(o, cached_fonts)
            if o.get_text() == 'я':
                x=1
        elif isinstance(o, Iterable):
            self.__correct_iterable_text(o, cached_fonts, fulltext)
        elif isinstance(o, LTTextLineHorizontal):
            self.__correct_line_text(o, fulltext)

    def __correct_char_text(self, char_obj: LTChar, cached_fonts: dict) -> None:
        char = char_obj.get_text()
        fontname = char_obj.fontname

        if not cached_fonts.get(fontname):
            self.__apply_match_dict(char_obj, fontname, char)
            return

        index = self.__get_char_index(char)
        if index is None:
            char_obj._text = char if char != "’" else "'"
            return

        self.__apply_correct_glyph(char_obj, fontname, index, cached_fonts)

    def __get_char_index(self, char: str) -> Optional[int]:
        if "cid" in char:
            return int(char[1:-1].split(":")[-1])
        elif "glyph" in char:
            glyph_unicode = int(char[5:])
            return ord(self.__unicodemaps[glyph_unicode])
        try:
            return ord(char)
        except Exception:
            return None

    def __apply_match_dict(self, char_obj: LTChar, fontname: str, char: str) -> None:
        try:
            char_obj._text = self.match_dict[fontname][char]
        except Exception:
            char_obj._text = char

    def __apply_correct_glyph(self, char_obj: LTChar, fontname: str, index: int, cached_fonts: dict) -> None:
        try:
            glyph_name = cached_fonts[fontname][index]
            actual_code = self.__name2code[fontname][glyph_name]
            unicode_char = self.match_dict[fontname][chr(actual_code)]
            char_obj._text = unicode_char
            if fontname not in self.__glyph_to_unicode:
                self.__glyph_to_unicode[fontname] = {}
            self.__glyph_to_unicode[fontname][glyph_name] = unicode_char
        except Exception:
            char_obj._text = " "

    def __correct_iterable_text(self, iterable: Iterable, cached_fonts: dict, fulltext: list) -> None:
        for item in iterable:
            self.__correct_pages_text(item, cached_fonts, fulltext)

    def __correct_line_text(self, line: LTTextLineHorizontal, fulltext: list) -> None:
        text = line.get_text()
        line._text = correct_string_incorrect_chars(text)
        fulltext.append(line.get_text())

    def get_correct_layout(self, pdf_path: Path) -> List[list]:

        self.text = ""
        self.match_dict = {}
        with tempfile.TemporaryDirectory() as fonts_temp_dir, tempfile.TemporaryDirectory() as glyphs_temp_dir:
            fonts_temp_path = Path(fonts_temp_dir)
            glyphs_temp_path = Path(glyphs_temp_dir)
            self.__read_pdf(pdf_path, fonts_temp_path, glyphs_temp_path)
            self.__match_glyphs_and_encoding_for_all(fonts_temp_path, glyphs_temp_path)

        layouts = self.__restore_layout(pdf_path)
        good_pdf_path = self.__process_pdf(str(pdf_path))
        return [layouts, good_pdf_path]

    def __restore_layout(self, pdf_path: Path, start: int = 0, end: int = 0) -> List[list]:
        self.__cached_fonts = {}
        self.__fontname2basefont = {}
        self.__unicodemaps = {}

        with open(pdf_path, "rb") as fp:
            parser = PDFParser(fp)
            document = PDFDocument(parser)
            pages_count = resolve1(document.catalog["Pages"])["Count"]
            end = pages_count if end == 0 else end

            rsrcmgr = PDFResourceManager()
            laparams = LAParams()
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            fixed_layouts = []
            pages = []

            for page_num, page in enumerate(PDFPage.create_pages(document)):
                if page_num < start:
                    continue
                elif page_num >= end:
                    break

                interpreter.process_page(page)
                layout = device.get_result()
                cached_fonts = {}
                fonts = page.resources.get("Font", {})

                for _, font_obj in fonts.items():
                    font_dict = resolve1(font_obj)
                    encoding = resolve1(font_dict.get("Encoding"))
                    f = rsrcmgr.get_font(objid=font_obj.objid, spec=font_obj.objid)
                    self.__fontname2basefont[f.fontname] = getattr(f, "basefont", f.fontname)

                    if hasattr(f, "unicode_map") and hasattr(f.unicode_map, "cid2unichr"):
                        basefont = self.__fontname2basefont[f.fontname]
                        self.__unicodemaps[basefont] = f.unicode_map.cid2unichr

                    if isinstance(encoding, dict) and ("Differences" in encoding or "/Differences" in encoding):
                        cached_fonts[f.fontname] = [
                            q.name if isinstance(q, PSLiteral) else q
                            for q in encoding.get("Differences", [])
                        ]
                    else:
                        cached_fonts[f.fontname] = []
                # Заменил потом надо переписать нормально
                # self.__cached_fonts = cached_fonts
                for fontname, differences in cached_fonts.items():
                    self.__cached_fonts.setdefault(fontname, differences)

                # self.__cached_fonts = rsrcmgr._cached_fonts
                fulltext = []
                self.__correct_pages_text(layout, cached_fonts, fulltext)
                fixed_layouts.append(layout)
                pages.append(page)

        return [pages, fixed_layouts]

    def save_corrected_pdf(self, input_path: Path, output_path: Path, pages_info: List[list]) -> None:
        """
        Сохраняет исправленный текст в новый PDF с поддержкой кириллицы
        :param input_path: путь к исходному PDF (для размеров страниц)
        :param output_path: путь для сохранения исправленного PDF
        :param pages_info: результат работы __restore_layout ([pages, fixed_layouts])
        """
        pages, layouts = pages_info

        with fitz.open(input_path) as src_doc, fitz.open() as new_doc:
            cyrillic_font = "Times-Roman"

            for page, layout in zip(src_doc, layouts):
                new_page = new_doc.new_page(
                    width=page.rect.width,
                    height=page.rect.height
                )

                def collect_text(element, text_items: list):
                    if isinstance(element, LTChar):
                        text_items.append({
                            'text': element._text,
                            'x': element.x0,
                            'y': page.rect.height - element.y1,
                            'size': element.size
                        })
                    elif hasattr(element, '__iter__'):
                        for child in element:
                            collect_text(child, text_items)

                text_items = []
                collect_text(layout, text_items)

                from collections import defaultdict
                lines = defaultdict(list)
                for item in text_items:
                    y = round(item['y'], 1)
                    lines[y].append(item)

                for y, items in sorted(lines.items(), reverse=True):
                    items.sort(key=lambda x: x['x'])
                    line_text = ''.join(item['text'] for item in items)

                    if line_text.strip():
                        try:
                            new_page.insert_text(
                                point=(items[0]['x'], y),
                                text=line_text,
                                fontsize=items[0]['size'],
                                fontname=cyrillic_font
                            )
                        except Exception as e:
                            print(f"Ошибка вставки текста: {e} | Текст: '{line_text}'")

            new_doc.save(output_path, garbage=4, deflate=True)

    def __process_pdf(self, pdf_path: str) -> str:
        import fitz
        import tempfile
        import os

        pdf_doc = fitz.open(pdf_path)

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            output_path = tmp_file.name

        try:
            for font_name, char_map in self.match_dict.items():
                if font_name in self.__pdf_fonts_dict:
                    cmap_str = self.generate_cmap(char_map, font_name)
                    font_xref = self.__pdf_fonts_dict[font_name]["xref"]
                    self.__add_tounicode_cmap_to_font(pdf_doc, font_xref, cmap_str)
                    print(f"Added cmap for font {font_name}")
                else:
                    print(f"Font {font_name} not found in PDF")

            pdf_doc.save(output_path)
            return output_path

        finally:
            pdf_doc.close()

    # def generate_cmap(match_dict_for_font: Dict[str, str]) -> str:
    #     # match_dict_for_font: mapping from glyph codes (str or int) to unicode chars (str)
    #     bfchar_lines = []
    #     for glyph_code, unicode_char in match_dict_for_font.items():
    #         # glyph_code — это строка, обычно имя глифа, нужно преобразовать в код (CID) — обычно integer
    #         # Для примера пусть glyph_code — это символ, берем ord
    #         # unicode_char — один символ
    #         cid = ord(glyph_code) if len(glyph_code) == 1 else int(glyph_code)
    #         uni = ord(unicode_char)
    #         bfchar_lines.append(f"<{cid:04X}> <{uni:04X}>")
    #
    #     cmap_text = f"""
    #         /CIDInit /ProcSet findresource begin
    #         12 dict begin
    #         begincmap
    #         /CIDSystemInfo
    #         << /Registry (Adobe)
    #         /Ordering (UCS)
    #         /Supplement 0
    #         >> def
    #         /CMapName /Adobe-Identity-UCS def
    #         /CMapType 2 def
    #         1 begincodespacerange
    #         <0000> <FFFF>
    #         endcodespacerange
    #         {len(bfchar_lines)} beginbfchar
    #         """ + "\n".join(bfchar_lines) + """
    #         endbfchar
    #         endcmap
    #         CMapName currentdict /CMap defineresource pop
    #         end
    #         end
    #         """
    #     return cmap_text
    # def __add_tounicode_cmap_to_font(self, pdf_doc: fitz.Document, font_xref, cmap_str):
    #     # to_unicode_xref = pdf_doc.add_stream(cmap_str.encode("utf-8"), info={"Type": "/Stream", "Length": len(cmap_str)})
    #     # font_obj = pdf_doc.get_obj(font_xref)
    #     # font_obj.update({"/ToUnicode": to_unicode_xref})
    #     cmap_xref = pdf_doc.get_new_xref()
    #     cmap_bytes = cmap_str.encode("utf-8")
    #     length = len(cmap_bytes)
    #     # obj_str = (
    #     #     f"<< /Length {length} >>\n"
    #     #     f"stream\n"
    #     #     f"{cmap_str}\n"
    #     #     f"endstream"
    #     # )
    #     import zlib
    #     obj_str = (
    #         f"<< /Length {length} >>\n"
    #         f"stream\n"
    #         f"{cmap_str}\n"
    #         f"endstream\n"
    #     )
    #     pdf_doc.update_object(cmap_xref, obj_str)
    #
    #     font_obj_str = pdf_doc.xref_object(font_xref, compressed=False)
    #
    #     insert_pos = font_obj_str.rfind(">>")
    #     if insert_pos == -1:
    #         raise ValueError("Invalid font object dictionary")
    #
    #     to_unicode_str = f"/ToUnicode {cmap_xref} 0 R\n"
    #     new_font_obj_str = font_obj_str[:insert_pos] + to_unicode_str + font_obj_str[insert_pos:]
    #     pdf_doc.update_object(font_xref, new_font_obj_str)

    def __add_tounicode_cmap_to_font(self, pdf_doc: fitz.Document, font_xref, cmap_str):
        cmap_bytes = cmap_str.encode("utf-8")

        cmap_xref = pdf_doc.get_new_xref()

        pdf_doc.update_object(
            cmap_xref,
            f"<< /Length {len(cmap_bytes)} >>"
        )

        pdf_doc.update_stream(cmap_xref, cmap_bytes)

        font_obj_str = pdf_doc.xref_object(font_xref, compressed=False)
        insert_pos = font_obj_str.rfind(">>")
        if insert_pos == -1:
            raise ValueError("Invalid font object dictionary")

        to_unicode_str = f"\n/ToUnicode {cmap_xref} 0 R\n"
        new_font_obj_str = font_obj_str[:insert_pos] + to_unicode_str + font_obj_str[insert_pos:]

        pdf_doc.update_object(font_xref, new_font_obj_str)




    def generate_cmap(self, char_map: Dict, font_name):
        """
        Генерирует ToUnicode CMap из словаря char_map {pdf_char: unicode_char}
        """
        bfchar_lines = []
        glyph_to_unicode = self.__glyph_to_unicode.get(font_name, {})
        differences = self.__cached_fonts[font_name]

        if glyph_to_unicode and differences:
            start_cid = differences[0]
            glyph_names = differences[1:]
            for offset, glyph_name in enumerate(glyph_names):
                cid = start_cid + offset

                uni_char = glyph_to_unicode.get(glyph_name)
                if uni_char is None:
                    uni_char = ' '
                if uni_char:
                    cid_hex = f"{cid:02X}"
                    uni_hex = f"{ord(uni_char):04X}"
                    bfchar_lines.append(f"<{cid_hex}> <{uni_hex}>")
        else:
            for pdf_char, uni_char in char_map.items():
                pdf_code = f"{ord(pdf_char):02X}"
                uni_code = f"{ord(uni_char):04X}"
                bfchar_lines.append(f"<{pdf_code}> <{uni_code}>")

        header = (
            "/CIDInit /ProcSet findresource begin\n"
            "12 dict begin\n"
            "begincmap\n"
            "/CIDSystemInfo\n"
            "<< /Registry (Adobe)\n"
            "/Ordering (UCS)\n"
            "/Supplement 0\n"
            ">> def\n"
            "/CMapName /Adobe-Identity-UCS def\n"
            "/CMapType 2 def\n"
            "1 begincodespacerange\n"
            "<00> <FF>\n"
            "endcodespacerange\n"
        )

        bfchar_block = f"{len(bfchar_lines)} beginbfchar\n" + "\n".join(bfchar_lines) + "\nendbfchar\n"

        footer = "endcmap\nCMapName currentdict /CMap defineresource pop\nend\nend"

        return header + bfchar_block + footer
