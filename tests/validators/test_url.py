from util import case


@case({
    "url": {
        "valid": [
            "http://tool.lu/regex/",
            "https://github.com/guyskk/validator",
            "https://avatars3.githubusercontent.com/u/6367792?v=3&s=40",
            "https://github.com",
            "//cdn.bootcss.com/bootstrap/4.0.0-alpha.3/css/bootstrap.min.css"
        ],
        "invalid": [
            None,
            "",
            "mail@qq.com",
            "google",
            "readme.md",
            "github.com",
            "www.google.com",
            b"https://github.com"
        ]
    }
})
def test_url():
    pass
