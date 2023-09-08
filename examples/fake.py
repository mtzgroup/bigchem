from bigchem.tasks import fake

try:
    r = fake()
except Exception as e:
    exc = e
    print(e.extra)

# try:
#     fr = fake.delay()
#     r = fr.get()
# except Exception as e:
#     exc = e
#     import pdb; pdb.set_trace()
#     print(e.extra)
