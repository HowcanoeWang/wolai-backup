import json
import pandas as pd

def get_root_index(getUserData):
    workspace = {}
    pages = pd.DataFrame(columns=['id', 'name', 'create_time', 'edit_time', 'outdated', 'workspace'])

    for w in getUserData['data']['workspaces']:
        workspace[w['id']] = w['name']
        
        for p in w['pages']:
            page = getUserData['data']['blocks'][p]
            pages.loc[len(pages), :] = [page['id'], 
                                        page['attributes']['title'][0][0], 
                                        page['created_time'], 
                                        page['edited_time'],
                                        False,
                                        w['name']]

    return workspace, pages


def get_pages_from_chunks(getPageChunks, workspace):
    pages = pd.DataFrame(columns=['id', 'name', 'create_time', 'edit_time', 'outdated', 'workspace'])

    for b_key, b_text in getPageChunks['data']['block'].items():
        block = b_text['value']
        if block['type'] == 'page':
            pages.loc[len(pages), :] = [block['id'], 
                                        block['attributes']['title'][0][0], 
                                        block['created_time'], 
                                        block['edited_time'],
                                        False,
                                        workspace[block['workspace_id']]]
    return pages


if __name__ == '__main__':
    with open('test_data/user_data.json', 'r') as f:
        user_data = json.load(f)

    workspace, pages = get_root_index(user_data)

    print(workspace)

    print('workspace-level: \n', pages)

    with open('test_data/page_chunks.json', 'r') as f:
        page_chunks = json.load(f)

    pages = get_pages_from_chunks(page_chunks, workspace)

    print('page-level: \n', pages)

