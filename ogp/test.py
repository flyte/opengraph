# encoding: utf-8

import unittest

from . import OpenGraph

HTML = """
<html xmlns:og="http://ogp.me/ns#">
<head>
<title>The Rock (1996)</title>
<meta property="og:title" content="The Rock" />
<meta property="og:type" content="movie" />
<meta property="og:url" content="http://www.imdb.com/title/tt0117500/" />
<meta property="og:image" content="http://ia.media-imdb.com/images/rock.jpg" />
</head>
</html>
"""


class test(unittest.TestCase):
    def test_url(self):
        data = OpenGraph(url="https://vimeo.com/896837")
        self.assertEqual(data.items["url"], "https://vimeo.com/896837")

    def test_isinstace(self):
        data = OpenGraph()
        self.assertTrue(isinstance(data, OpenGraph))

    def test_to_html(self):
        og = OpenGraph(html=HTML)
        self.assertTrue(og.to_html())

    def test_is_valid(self):
        og = OpenGraph(url="http://github.com")
        self.assertTrue(og.is_valid())

    def test_is_not_valid(self):
        og = OpenGraph(url="http://itcorp.com/")
        self.assertFalse(og.is_valid())

    def test_required(self):
        og = OpenGraph(
            url="http://example.com", required_attrs=("description",), scrape=True
        )
        self.assertTrue(og.is_valid())

    def test_scrape(self):
        og = OpenGraph(
            url="http://graingert.co.uk/", required_attrs=("description",), scrape=True
        )
        self.assertTrue(og.is_valid())
        self.assertTrue(og.items["description"])

        og = OpenGraph(
            url="http://www.crummy.com/software/BeautifulSoup/bs3/documentation.html",
            required_attrs=("description",),
            scrape=True,
        )
        self.assertEqual(og.items["description"], "Beautiful Soup Documentation")

    def test_absolute(self):
        og = OpenGraph(
            url="http://www.crummy.com/software/BeautifulSoup/bs3/documentation.html",
            required_attrs=("image",),
            scrape=True,
        )
        self.assertEqual(
            og.items["image"], "http://www.crummy.com/software/BeautifulSoup/bs3/6.1.jpg"
        )

    def test_missing_head(self):
        og = OpenGraph(html="<html><body></body></html>", scrape=True)
        self.assertEqual(og.items["title"], None)

    def test_missing_body(self):
        og = OpenGraph(html="<html><head></head></html>", scrape=True)
        self.assertEqual(og.items["title"], None)

    def test_missing_head_and_body(self):
        og = OpenGraph(html="<html></html>", scrape=True)
        self.assertEqual(og.items["title"], None)


if __name__ == "__main__":
    unittest.main()
