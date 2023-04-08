import json
import logging
from pathlib import Path
from typing import Any, Dict

import arxiv
from arxiv import Result

from papercast.types import PathLike, PDFFile
from papercast.production import Production
from papercast.base import BaseProcessor

logging.basicConfig(level=logging.INFO)


class ArxivProcessor(BaseProcessor):
    input_types = {"arxiv_id": str}
    output_types = {
        "pdf": PDFFile,
        "title": str,
        "arxiv_id": str,
        "authors": list,
        "doi": str,
        "description": str,
    }


    def __init__(self, pdf_dir: PathLike, json_dir: PathLike):
        self.pdf_dir = pdf_dir
        self.json_dir = json_dir

    def process(self, production: Production, **kwargs) -> Production:
        pdf_path, json_path, doc = self._download_and_create_json_arxiv(production.arxiv_id) # type: ignore
        pdf = PDFFile(path=pdf_path)
        setattr(production, "pdf", pdf)
        for k, v in doc.items():
            setattr(production, k, v)
        return production

    def get_arxiv_result(self, arxiv_id: str) -> Result:
        return next(arxiv.Search(id_list=[arxiv_id]).results())

    def _download_and_create_json_arxiv(
        self,
        arxiv_id: str,
    ):
        doc = {}
        result = self.get_arxiv_result(arxiv_id)
        pdf_path = result.download_pdf(dirpath=str(self.pdf_dir))

        doc["pdf"] = PDFFile(pdf_path)
        doc["title"] = result.title
        doc["arxiv_id"] = result.entry_id
        doc["authors"] = list(
            str(result.authors).split("'")[1::2]
        )  # remove "arxiv.Result.Author('", "')"
        doc["doi"] = result.doi
        doc["description"] = result.summary.replace("\n", " ")

        logging.info(f"Downloaded pdf to {pdf_path}")

        return pdf_path, None, doc
