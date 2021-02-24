import os
import shutil
import sys
import hashlib

username = ''
blacklist = ['.gnupg', '.thunderbird', '.bash_logout', '.pki', '.mozilla', '.java', '.sudo_as_admin_successful',
             '.cache', '.steampid', '.pulse-cookie', '.apport-ignore', '.ssh', '.profile', '.local', 'bash_history',
             '.config', 'snap', 'Julkinen', 'Public', '.bash_history', '.apport-ignore.xml', '.steampath', '.steam',
             '.bashrc', '.minecraft']
backup_path = ''
media_path = ''
home_path = ''
debug = True
Total_file_size = 0
number_of_drives = 0
f1 = ''


# check if we are using linux
def os_check():
    global username, debug, Total_file_size, number_of_drives, number_of_zips
    if sys.platform == "linux" or sys.platform == "linux2":
        print('')
        print('--------------------------------------------------------------------------------')
        print('Linux OS detected')
        print('--------------------------------------------------------------------------------')
        print('')
        main()
        print('')
        print('--------------------------------------------------------------------------------')
        print('')
    else:
        print('Platform not supported:', sys.platform)
        input('Press Enter To continue')
        sys.exit(1)
    print('Backup Completed Successfully')
    if Total_file_size != 0 and number_of_drives != 0:
        print('Total', alt_file_check(Total_file_size / number_of_drives))
    else:
        print('Files are already up to date')
    if number_of_drives != 0:
        print("Number of Backup Drives used:", number_of_drives)
    else:
        print('No backup drives created/found')
    if not debug:
        input("Press Enter to continue...")


# end check
# begin main program
def main():
    global username, media_path, home_path
    for users in os.listdir('/home'):  # check each user
        username = users
        media_path = os.path.join('/media', username)
        home_path = os.path.join('/home', username)
        os.chdir(home_path)
        print('Doing backup for user:', username.capitalize())
        Find_drives()


# end main

def file_size_check(file_in):
    global Total_file_size
    size = os.path.getsize(file_in)
    Total_file_size += size
    return alt_file_check(size)


def alt_file_check(size, byte_order=''):
    if size < 1024:
        size = size
        byte_order = 'bytes'
    elif size < 1048576:
        size = size / 1024
        byte_order = 'KB'
    elif size < 1073741824:
        size = size / 1048576
        byte_order = 'MB'
    elif size < 1099511627776:
        size = size / 1073741824
        byte_order = 'GB'
    elif size < 1125899906842624:
        size = size / 1099511627776
        byte_order = 'TB'
    if size > 99:
        rumlen = str(size)[0:3]
    elif 99 > size > 10:
        rumlen = str(size)[0:2]
    else:
        rumlen = str(size)[0:1]
    return 'File Size: ' + rumlen + ' ' + byte_order


def Find_drives():
    global number_of_drives, username, media_path, home_path, debug, backup_path
    if debug:
        print('User:', username, '\nMedia path:', media_path, '\nHome Path:', home_path)
    for drive in os.listdir(media_path):
        backup_path = os.path.join(media_path, drive, 'FS_Backup', 'Linux', 'Home_Directory')
        number_of_drives += 1
        if not os.path.exists(backup_path):
            os.makedirs(backup_path)
        if debug:
            print('Using Drive:', drive, '\nBackup folder:', backup_path)
        blacklist_check()


def blacklist_check():
    global home_path, blacklist
    for zips in os.listdir(home_path):
        if zips not in blacklist:
            md5_check(zips)


def get_dir_hash(directory, verbose=0):
    global f1
    sha_hash = hashlib.md5()
    if not os.path.exists(directory):
        return -1
    try:
        for root, dirs, files in os.walk(directory):
            for names in files:
                if verbose == 1:
                    print('Hashing', names)
                filepath = os.path.join(root, names)
                try:
                    f1 = open(filepath, 'rb')
                except:
                    # You can't open the file for some reason
                    f1.close()
                    continue
                while 1:
                    # Read file in as little chunks
                    buf = f1.read(4096)
                    if not buf:
                        break
                    sha_hash.update(hashlib.md5(buf).digest())
                f1.close()
    except:
        import traceback
        # Print the stack traceback
        traceback.print_exc()
        return -2
    return sha_hash.hexdigest()


def md5_check(zip_file):
    global backup_path, debug
    md5 = get_dir_hash(zip_file)
    if not os.path.exists(os.path.join(backup_path, zip_file + '.md5')):
        with open(os.path.join(backup_path, zip_file + '.md5'), 'w') as f:
            f.write(str(md5))
            f.close()
        make_zip(zip_file)
    with open(os.path.join(backup_path, zip_file + '.md5'), 'r') as file:
        old_md5 = file.read()
    if not old_md5 == md5:
        with open(os.path.join(backup_path, zip_file + '.md5'), 'w') as f:
            f.write(str(md5))
            f.close()
        if debug:
            print('Old md5:', old_md5, '\nNew md5:', md5)
        make_zip(zip_file)


def make_zip(file):
    global home_path, backup_path
    print(get_dir_size(os.path.join(home_path, file)))
    shutil.make_archive(file, 'xztar', os.path.join(home_path, file))
    shutil.move(home_path + '/' + file + '.tar.xz', backup_path + '/' + file + '.tar.xz')


def get_dir_size(start_path='.'):
    global Total_file_size
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    Total_file_size += total_size
    return alt_file_check(total_size)


if __name__ == '__main__':
    os_check()
