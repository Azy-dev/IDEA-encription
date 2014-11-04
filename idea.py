def add(a, b):
    return (a+b)% 65536


def multiply(a, b):
    if a == 0:
        a = 65536
    if b == 0:
        b = 65536
    if (a*b) % 65537 == 65536:
        return 0
    else:
        return (a*b)%65537

def extended_euclidean(a, b):
#раширенный алгоритм Евклида.
#возвращает (gcd(a,b), x, y), такие что gcd(a,b)= a*x + b*y
    assert a != 0 or b != 0
    a0, a1, b0, b1 = 1, 0, 0, 1
    while b != 0:
        q, r = divmod(a, b) # q - целое от деления, r - остаток
        a, b = b, r
        a0, a1, b0, b1 = b0, b1, a0 - q*b0, a1 - q*b1
    return [a, a0, a1]

def multipl_inverse(x):
    p = 65537
    if x == 0:
        return p
    a,y,b = extended_euclidean(x,p)
    if y >= 0:
        return y
    if y < 0:
        return (y + 65537)

def cyclic_left_shift(key, m):
#производит циклический сдвиг ключа на m влево
    return key[m:]+key[:m]

def eight_subkeys(key):
#разбивает 128-битный ключ на 8 16-битных подключа
    K=[]
    for i in range( 8 ) :
        K = K + [key[(i*16):((i+1)*16)]]
    return K

def subkeys_gen(key):
#вычисляет 52 16-битных подключа шифрования

    #приводим ключ к 128-битному двоичному выражению
    key_with_extra_bit = key+ 2**128
    key_128bit = bin(key_with_extra_bit)[3:]
    #генерация первых 48-ми подключей
    shifted_key = key_128bit
    K = []
    for j in range (6):
        K = K + eight_subkeys(shifted_key)
        shifted_key = cyclic_left_shift(shifted_key, 25)
    #генерация последних 4-х подключей
    K = K + eight_subkeys(shifted_key)[0:4]
    #переводим ключи из "бинарного" текста в числа
    for i in range (52):
        K[i] = '0b' + K[i]
        K[i] = int(K[i], 2)
    return K

def decryption_subkeys(K):
#вычисляет 52 16-битных подключа дешифрования
    p = 65536
    L = [0]*52
    L[0] = multipl_inverse(K[48])
    L[1] = p - K[49]
    L[2] = p - K[50]
    L[3] = multipl_inverse(K[51])
    L[4] = K[46]
    L[5] = K[47]

    for i in range(1,8):
        L[0 + 6*i] = multipl_inverse(K[48 - 6*i])
        L[1 + 6*i] = p - (K[50 - 6*i])
        L[2 + 6*i] = p - (K[49 - 6*i])
        L[3 + 6*i] = multipl_inverse(K[51 - 6*i])
        L[4 + 6*i] = K[46 - 6*i]
        L[5 + 6*i] = K[47 - 6*i]

    L[48] = multipl_inverse(K[0])
    L[49] = p - (K[1])
    L[50] = p - (K[2])
    L[51] = multipl_inverse(K[3])

    return L



def idea_algorythm(text,K):

    #разбиваем блок текста на 4 числовых подблока
    A = ord(text[0])
    B = ord(text[1])
    C = ord(text[2])
    D = ord(text[3])
        
    #шифруем 4 подблока
    for j in range (8):
        A = multiply(A, K[j*6 + 0])
        B = add     (B, K[j*6 + 1])
        C = add     (C, K[j*6 + 2])
        D = multiply(D, K[j*6 + 3])
        E = A^C
        F = B^D
        E = multiply(E, K[j*6 + 4])
        F = add(F, E)
        F = multiply(F, K[j*6 +5])
        E = add(E, F)
        A = A^F
        C = C^F
        B = B^E
        D = D^E
        if j < 7:
            B,C = C,B
    #заключительный 9-й раунд
    A = multiply(A, K[48])
    B = add(B, K[49])
    C = add(C, K[50])
    D = multiply(D, K[51])

    return chr(A) + chr(B) + chr(C) + chr(D)


#программа шифрования и расшифровки текста по алгоритму IDEA
#
#шифрование
import random
key = random.getrandbits(128)
print('key =', key, '\n')
K = subkeys_gen(key)

text = input('введите текст: ')
r = len(text) % 4
text = text + 'x' * (4 - r) #делаем длину текста кратной 4-м
N = len(text)//4
c_text = ''
for j in range(N):
    text_block = [text[4*j + m] for m in range(4)] 
    c_text_block = idea_algorythm(text_block, K)
    c_text = c_text + c_text_block
print('зашифрованный текст:', c_text)

#расшифровка
L = decryption_subkeys(K)
text = ''
for j in range(N):
    c_text_block = [c_text[4*j + m] for m in range(4)]
    text_block = idea_algorythm(c_text_block, L)
    text = text + text_block
text = text[:-(4 - r)]
print('расшифрованный текст:', text)

