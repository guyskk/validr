from util import case

# 手机号码测试用例
# http://blog.csdn.net/mr_lady/article/details/50245223
phone_headers = [133, 153, 180, 181, 189, 177, 130, 131, 132,
                 155, 156, 145, 185, 186, 176, 185, 134, 135,
                 136, 137, 138, 139, 150, 151, 152, 158, 159,
                 182, 183, 184, 157, 187, 188, 147, 178]
valid_phone = ['%d87654321' % x for x in phone_headers]
valid_phone.extend(['+86%s' % x for x in valid_phone[:5]])

invalid_phone = ['%d87654321' for x in range(10, 20)
                 if x not in [13, 14, 15, 17, 18]]
invalid_phone.extend([
    '1331234567',
    '1331234',
    '1331234567x',
    '13312345678x',
    'x1331234567',
    '.1331234567',
    '#1331234567',
    '13312345678 ',
    ' 13312345678',
    '1331234 5678'
])


@case({
    'phone': {
        'valid': valid_phone,
        'invalid': invalid_phone
    }
})
def test_phone():
    pass
