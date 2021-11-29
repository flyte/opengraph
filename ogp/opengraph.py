# encoding: utf-8

import re
from contextlib import closing
from typing import Any, Dict, Iterable, Optional, Set, Union
from urllib.parse import urljoin
from urllib.request import urlopen

from bs4 import BeautifulSoup


class OpenGraph:
    scrape: bool = False

    def __init__(
        self,
        url: str = "http://example.com",
        html: Optional[str] = None,
        scrape: bool = False,
        required_attrs: Iterable[str] = set(("title", "type", "image", "url")),
        **kwargs: Any,
    ):
        # If scrape == True, then will try to fetch missing attribtues
        # from the page's body
        self.scrape = scrape
        self.url = url
        self.items: Dict[str, Optional[str]] = {}
        self.required_attrs: Set[str] = set(required_attrs)

        if not html:
            with closing(urlopen(url, **kwargs)) as raw:
                html = raw.read()

        self.parse(html)

    def absolute(self, url: str) -> str:
        return urljoin(self.url, url)

    def parse(self, html: Union[str, BeautifulSoup]) -> None:
        if not isinstance(html, BeautifulSoup):
            doc = BeautifulSoup(html, features="html.parser")
        else:
            doc = html

        # Not a lot we can do if there's no HTML
        if doc.html is None:
            return

        if doc.html.head is not None:
            ogs = doc.html.head.findAll(property=re.compile(r"^og"))
            for og in ogs:
                if og.has_attr("content"):
                    self.items[og["property"][3:]] = og["content"]

        # Couldn't fetch all attrs from og tags, try scraping body
        if self.scrape:
            remaining_keys = self.required_attrs - set(self.items.keys())
            for key in remaining_keys:
                self.items[key] = getattr(self, "scrape_{key}".format(key=key))(doc)

        image = self.items.get("image", False)
        if image:
            self.items["image"] = self.absolute(self.items["image"])

    def is_valid(self) -> bool:
        return self.required_attrs <= set(self.items.keys())

    def to_html(self) -> str:
        if not self.is_valid():
            return '<meta property="og:error" content="og metadata is not valid" />'

        meta = ""
        for key, value in self.items.items():
            meta += '\n<meta property="og:%s" content="%s" />' % (key, value)
        meta += "\n"

        return meta

    def scrape_image(self, doc: BeautifulSoup) -> Optional[str]:
        if doc.html.body is None:
            return None
        images = [dict(img.attrs)["src"] for img in doc.html.body.findAll("img")]

        if images:
            return images[0]

        return None

    def scrape_title(self, doc: BeautifulSoup) -> Optional[str]:
        if doc.html.head is None:
            return None
        if doc.html.head.title is None:
            return None
        return doc.html.head.title.text

    def scrape_type(self, _: BeautifulSoup) -> str:
        return "other"

    def scrape_url(self, _: BeautifulSoup) -> str:
        return self.url

    def scrape_description(self, doc: BeautifulSoup) -> Optional[str]:
        if doc.html.head is None:
            return None
        ogs = doc.html.head.findAll(
            name="meta",
            attrs={"name": ("description", "DC.description", "eprints.abstract")},
        )
        for og in ogs:
            content = og.get("content", False)
            if content:
                return content
        else:
            heading = doc.html.find(re.compile("h[1-6]"))
            if heading:
                return heading.text
            else:
                return doc.html.find("p").text
