# -*- encoding: utf-8 -*-

# python apps
import chardet
import magic
import os


def analysis_filename(f_name):
    '解析文件名'
    s_dir = s_name = base_name = ext_name = None
    s_dir, s_name = os.path.split(f_name)
    if s_name:
        base_name, ext_name = os.path.splitext(s_name)
    return (s_dir, s_name, base_name, ext_name)


def bytes_decode(msg_b, arr_code=None):
    """ bytes解码
        msg_b           字符串的二进制格式
        arr_code        编码的名称
    """
    if not isinstance(msg_b, bytes) or len(msg_b) == 0:
        return msg_b

    if arr_code is None:
        info_chardet = chardet.detect(msg_b)
        arr_code = (info_chardet['encoding'],)
    elif not hasattr(arr_code, '__iter__'):
        arr_code = [arr_code]

    for code in arr_code:
        try:
            s = msg_b.decode(code)
            break
        except UnicodeDecodeError:
            pass
    else:
        raise UnicodeDecodeError
    return s


def check_filename_length(filename):
    """ 检查文件名超长 """
    if isinstance(f_name, str):
        n = len(f_name.encode())
    elif isinstance(f_name, bytes):
        n = len(f_name)
    else:
        msg = "文件名类型错误！filename: {}".format(filename)
        raise ValueError(msg)
    if 220 < n:
        f_name = "{}...{}".format(f_name[:20], f_name[-20:])
    else:
        f_name = f_name
    return f_name


def check_filename_repeat(f_name):
    '检查文件名重复'
    s_dir, s_name, base_name, ext_name = analysis_filename(f_name)
    filename = f_name
    i = 0
    while os.path.exists(output_name):
        # 文件存在
        i = i + 1
        s_name = "{}_{}{}".format(base_name, i, ext_name)
        filename = os.path.join(s_dir, s_name)
    return filename


def extract_email(f_name, msg_b=None, output_dir=None):
    ''' 展开文件的内容(news or email格式)
        f_name              文件名
        msg_b               文件内容(2进制格式)
        output_dir          输出目录
    '''
    arr_filename = []
    arr_error = []

    try:
        s_dir, s_name, base_name, ext_name = analysis_filename(f_name)
        if output_dir:
            path_root = os.path.join(output_dir, base_name.strip())
        else:
            path_root = os.path.join(s_dir, base_name.strip())
        if not os.path.exists(path_root):
            os.mkdir(path_root)

        if msg_b is None:
            with open(f_name, 'rb') as f:
                msg_b = f.read()

        info_chardet = chardet.detect(msg_b)
        msg = msg_b.decode(info_chardet['encoding'])
        obj_message = email.message_from_string(msg)

        for i, part in enumerate(obj_message.walk()):
            try:
                if part.get_content_maintype() == 'multipart':
                    continue
                data = part.get_payload(decode=True)
                s_name = part.get_filename()
                if not s_name:
                    ext = mimetypes.guess_extension(part.get_content_type())
                    if not ext:
                        s = magic.from_buffer(data)
                        arr = s.lower().split()
                        if arr:
                            ext = '.{}'.format(arr[0])
                        else:
                            ext = '.bin'
                    s_name = 'part-{}{}'.format(i, ext)
                filename = os.path.join(path_root, s_name)
                filename = check_filename_repeat(filename)
                with open(filename, 'wb') as f:
                    f.write(data)
                arr_filename.append(filename)
            except Exception as e:
                arr_error.append({'e': str(e), 'f_name': f_name, 'i': i})
    except Exception as e:
        arr_error.append({'e': str(e), 'f_name': f_name})

    return (arr_filename, arr_error)


