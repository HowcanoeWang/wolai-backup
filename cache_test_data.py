from main import Wolai
import json

if __name__ == '__main__':

    wolai = Wolai('userinfo.txt', 'backup', close_tab=True)

    #wolai.login()

    # save user data
    with open('test_data/user_data.json', 'w') as f:
        json.dump(wolai.get_user_data(), f)

    # save chunks
    with open('test_data/page_chunks.json', 'w') as f:
        json.dump(wolai.get_page_chunks('9j8Hg4NMLqe2s1saBXYXAa'), f)