## Kuwa Full Installation Guide for Linux

* OS version: Ubuntu 22.04 LTS

### 1. Install Docker

Refer to [Docker official installation documentation](https://docs.docker.com/engine/install/).

```sh=
# Uninstall conflicting packages
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done

# Add docker's official GPG key
sudo apt-get update
sudo apt-get install ca-certificates
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Setup repository
echo \
    "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
    "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

# Install necessary package
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Enable the service
sudo systemctl --now enable docker

# Enable unattended-update
cat <<EOT | tee /etc/apt/apt.conf.d/51unattended-upgrades-docker
    Unattended-Upgrade::Origins-Pattern {
        "origin=Docker";
    };
EOT
```

* Use `sudo docker run hello-world` to test if docker is installed successfully.

### 2. (Optional) Install NVIDIA Drivers

```shell=
# Update and Upgrade
sudo apt update
sudo apt upgrade

# Remove previous NVIDIA installation
sudo apt autoremove nvidia* --purge
sudo apt autoclean

# Install Ubuntu and NVIDIA drivers
ubuntu-drivers devices # get the recommended version
sudo ubuntu-drivers autoinstall
sudo apt install nvidia-driver-$version

# Reboot
sudo reboot
```

If reboot is unsuccessful, hold down `shift` key, select `Advanced options for Ubuntu > recovery mode > dpkg`, and follow the instructions to repair broken packages.

After reboot, use the command `nvidia-smi` to check if nvidia-driver is installed successfully.

possible result:

![](./img/docker_installation_1.png)

### 3. (Optional) Install CUDA Toolkits

Refer to [NVIDIA CUDA official installation guide](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/).

```sh=
# Update and Upgrade
sudo apt update
sudo apt upgrade

# Install CUDA toolkit
sudo apt install nvidia-cuda-toolkit

# Check CUDA install
nvcc --version
```
![](./img/docker_installation_2.png)

You can test CUDA on Pytorch:
```sh=
sudo apt-get install python3-pip
sudo pip3 install virtualenv 
virtualenv -p py3.10 venv
source venv/bin/activate

# Install pytorch
pip3 install torch torchvision torchaudio
pip install --upgrade pip

# Test
python3
```

(In python):
```python=
import torch
print(torch.cuda.is_available()) # should be True

t = torch.rand(10, 10).cuda()
print(t.device) # should be CUDA
```

expected result:

![](./img/docker_installation_3.png)

### 4. (Optional) Install NVIDIA Container Toolkit

Refer to [NVIDIA Container Toolkit official installation guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).

```sh=
# Setup GPG key
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

# Setup the repository
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Configure the NVIDIA runtime to be the default docker runtime
sudo nvidia-ctk runtime configure --runtime=docker --set-as-default
sudo systemctl restart docker
```

### 5. Install Kuwa

1. Download Kuwa Repository

```sh=
git clone https://github.com/kuwaai/genai-os/
cd genai-os/docker
```

2. Change Configuration Files

Copy `.admin-password.sample`, `.db-password.sample`, `.env.sample`, `run.sh.sample`, remove the `.sample` suffix to setup your own configuration files.

```sh=
cp .admin-password.sample .admin-password
cp .db-password.sample .db-password
cp .env.sample .env
```

* `.admin-password`: default administrator password
* `.db-password`: system built-in database password
* `.env`: environment variables, the default set value is as follows
```tx
DOMAIN_NAME=localhost # Website domain name, if you want to make the service public, please set it to your public domain name
PUBLIC_BASE_URL="http://${DOMAIN_NAME}/" # Website base URL

ADMIN_NAME="Kuwa Admin" # Website default administrator name
ADMIN_EMAIL="admin@${DOMAIN_NAME}" # Website default administrator login email, which can be an invalid email
```
* `run.sh`: the executable file

3. Start the System

Execute and wait for minutes.

```sh
sudo ./run.sh
```

By default, Kuwa will be deployed on `http://localhost`.

### 6. (Optional) Building Docker Images from Source Code

Since version 0.3.4, Kuwa Docker Images are downloaded pre-built from Docker Hub by default. To build images from source code, follow these steps:

1. Ensure the `.git` directory is present within the `genai-os` directory.
2. Enable the containerd image store for [multi-platform builds](https://docs.docker.com/build/building/multi-platform/#enable-the-containerd-image-store)
    Add the following configuration to your `/etc/docker/daemon.json` file:

    ```json
    {
      "features": {
        "containerd-snapshotter": true
      }
    }
    ```
    Restart the Docker daemon after saving the changes:
    ```sh
    sudo systemctl restart docker
    ```
3. **Build the Kuwa images using the following command:**
    ```sh
    sudo ./run.sh build
    ```

This command will create the following images: 

- `kuwaai/model-executor`
- `kuwaai/multi-chat`
- `kuwaai/kernel`
- `kuwaai/multi-chat-web`

### 7. (Optional) Setup HTTPS service

Since version 0.4.0, the docker version of Kuwa supporting automatically acquire the HTTPS certification from let's encrypt.
You can follow the following instruction to setup a HTTPS service.

1. Ensure you have setup the correct DNS record and the firewall allows both port 80 and port 443.
2. Edit `docker/.env` to set `DOMAIN_NAME` to your domain name (e.g. example.com)
3. Edit `docker/run.sh` to add `"https-auto"` to the `confs` array
4. Run the script `./run.sh`
5. The certification acquiring process should start automatically
6. Wait until the log shows
  ```
  letsencrypt-companion-1  | Reloading nginx (using separate container kuwa-web-1)...
  ```
7. As a known issue, you need to terminate the script manually then restart it again, otherwise the container "web" will repeating restarting.
8. Now you can access https://example.com/

### 7. (Optional) Setting Up HTTPS Service with Let's Encrypt

Starting with version 0.4.0, the Docker version of Kuwa offers automatic HTTPS certificate acquisition using Let's Encrypt. To set up your HTTPS service:

1. Ensure your domain name's DNS records are properly configured and your firewall allows traffic on ports 80 and 443.
2. In the `docker/.env` file, set the `DOMAIN_NAME` variable to your domain (e.g., `example.com`).
3. Modify the `docker/run.sh` script by adding `"https-auto"` to the `confs` array.
4. Run the `./run.sh` script. (You may need to run `./run.sh build web` first if the image isn't up-to-date).
5. The certificate acquisition process will begin automatically.
6. Watch for the following log message indicating successful configuration:
   ```
   letsencrypt-companion-1  | Reloading nginx (using separate container kuwa-web-1)...
   ```
7. Due to a known issue, you'll need to manually terminate the `run.sh` script and restart it to prevent the "web" container from repeatedly restarting.
8. Your site is now accessible via HTTPS at `https://example.com/`.