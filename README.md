# 1. Скачиваем установщик
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# 2. Устанавливаем его
sudo dpkg -i google-chrome-stable_current_amd64.deb

# 3. Исправляем зависимости, если потребуется
sudo apt-get -f install -y

# 4. Удаляем скачанный установщик, он больше не нужен
rm google-chrome-stable_current_amd64.deb


Действие: Создайте папку проекта и перейдите в нее.

mkdir -p /home/lev/projects/taxes-gov-az
cd /home/lev/projects/taxes-gov-az

python3 -m venv venv
source venv/bin/activate



pip install -r requirements.txt