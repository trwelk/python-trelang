import basic

while True:
    text = input('basic >')
    result, error = basic.run('Shell', text)

    if (error):
        print(error.__as_string__())
    else:
        print(result)
