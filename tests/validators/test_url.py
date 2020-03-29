from validr import T
from . import case


@case({
    T.url: {
        'valid': [
            'http://127.0.0.1:8080/hello?key=中文',
            'http://tool.lu/regex/',
            'https://github.com/guyskk/validator',
            'https://avatars3.githubusercontent.com/u/6367792?v=3&s=40',
            'https://github.com',
            'https://www.google.com/' + 'x' * 128,
        ],
        'invalid': [
            None,
            123,
            '',
            'mail@qq.com',
            'google',
            'readme.md',
            'github.com',
            'www.google.com',
            'https://www.google.com/' + 'x' * 256,
            b'https://github.com',
            'http：//www.google.com',
            '//cdn.bootcss.com/bootstrap/4.0.0-alpha.3/css/bootstrap.min.css',
        ]
    }
})
def test_url():
    pass
