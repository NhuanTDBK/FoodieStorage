import dropbox
import ConfigParser, os
from dropbox.files import FileMetadata, FolderMetadata
import datetime
import sched,time
from PIL import Image
from StringIO import StringIO

print "Reading config file"
config = ConfigParser.RawConfigParser()
config.read("default.cfg")
app_key=config.get("Dropbox","app_key")
app_secret=config.get("Dropbox","app_secret")
access_token = config.get("Dropbox","access_token")
# flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)
# authorize_url = flow.start()
# print '1. Go to: ' + authorize_url
# print '2. Click "Allow" (you might have to log in first)'
# print '3. Copy the authorization code.'
# code = raw_input("Enter the authorization code here: ").strip()
# access_token, user_id = flow.finish(code)
# config.set("Dropbox","access_token",access_token)
# config.write(open("default.cfg",'wb'))

client = dropbox.Dropbox(access_token)
print "Access to dropbox..."
def upload(dbx,folder,subfolder,name,overwrite=False):

    fullname = '%s/%s/%s' % (folder, subfolder.replace(os.path.sep, '/'), name)
    path = '/%s/%s/%s' % (folder, subfolder.replace(os.path.sep, '/'), name)
    while '//' in path:
        path = path.replace('//', '/')
    mode = (dropbox.files.WriteMode.overwrite
            if overwrite
            else dropbox.files.WriteMode.add)
    mtime = os.path.getmtime(fullname)
    with open(fullname, 'rb') as f:
        data = f.read()
    try:
        res = dbx.files_upload(
            data, path, mode,
            client_modified=datetime.datetime(*time.gmtime(mtime)[:6]),
            mute=True)
    except dropbox.exceptions.ApiError as err:
        print('*** API error', err)
        return None
    print('uploaded as', res.name.encode('utf8'))
    return res
def download(dbx, folder, subfolder, name):
    """Download a file.
    Return the bytes of the file, or None if it doesn't exist.
    """
    path = '/%s/%s/%s' % (folder, subfolder.replace(os.path.sep, '/'), name)
    while '//' in path:
        path = path.replace('//', '/')
    try:
        md, res = dbx.files_download_to_file("/storage/%s" % name, path)
    except dropbox.exceptions.HttpError as err:
        print('*** HTTP error', err)
        return None
    data = res.content
    # print(len(data), 'bytes; md:', md)
    im = Image.open(StringIO(data))
    return data
def delta():
    dbx = client
    current_list = set(os.listdir("storage"))
    server_list = set([t.name for t in dbx.files_list_folder("/storage").entries])
    diff_list = current_list - server_list
    if(len(diff_list)==0):
        return 0
    for diff_file in diff_list:
        upload(dbx,'storage',"",diff_file)
    return diff_list


def sync_folder():
    dbx = client
    server_list = set([t.name for t in dbx.files_list_folder("/storage").entries])
    print "Retrieving file list"
    for index, file_name in enumerate(server_list):
        print "%d / %d" % (index + 1, len(server_list))
        file_full_name = "%s/storage/%s" % (os.getcwd(), file_name)
        dbx.files_download_to_file(file_full_name, "/storage/" + file_name)
    return "OK"
def hello():
    print "hello"
def upload_folder():
    for dn,dirs,files in os.walk("storage"):
        print "Starting sync..."
        for name in files:
            print "Upload %s"%name
            upload(client,"storage","",name)
        print "Complete upload..."