# Comment Search Engine

## Project Structure

| Folder/File | Description |
|:-|:-|
| `cse` | source code for this project |
| `deployment` | tbd |
| `testData.csv` | validation data for the web crawler |

<!-- | `data` | downloaded data of the web crawler | -->


## Get it running

- Install VirtualBox 5.1.x from [Oracles download site](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1)
- Install Vagrant 2.0.x following [this guide](https://www.vagrantup.com/intro/getting-started/index.html)
- Use the following commands to bring up the vagrant box:

```bash
vagrant up
vagrant ssh
```

- install the project in the vagrant box

```bash
python setup.py sdist
sudo pip install --upgrade dist/CommentSearchEngine-0.1.0.tar.gz
```

- now you are able to use the Comment Search Engine
  - to use the web crawler type: 
  ```bash
  crawl <TODO>
  ```

- For testing you can use `python cse` to start the crawler (without installing the project). `python cse -h` will give you a hint about the different parameters.
## Vagrant

This project uses vagrant for environment setup and testing. Use `vagrant up` to start the testing environment.

## Dependencies

- Web Crawler
  - scrapy
