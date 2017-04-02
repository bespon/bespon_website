import os
import shutil

website_dir = os.path.abspath('site')
github_io_dir = os.path.abspath(os.path.join('..', 'bespon.github.io'))


for name in os.listdir(github_io_dir):
    if name != '.git':
        path = os.path.join(github_io_dir, name)
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path)


for name in os.listdir(website_dir):
    path = os.path.join(website_dir, name)
    if os.path.isfile(path):
        shutil.copy(path, github_io_dir)
    else:
        shutil.copytree(path, os.path.join(github_io_dir, name))

shutil.copy('CNAME', github_io_dir)
