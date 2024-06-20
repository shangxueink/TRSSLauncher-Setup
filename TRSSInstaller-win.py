import os
import subprocess
import shutil
from os import path
import tempfile
import json
from colorama import init, Fore
import socket
import psutil

def check_environment():
  try:
    node_version_output = subprocess.run(["node", "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    node_version = node_version_output.stdout.strip()
    major_version = int(node_version.split('.')[0][1:])
    print(f"Node.js 版本: {node_version}  √")
    if major_version < 18:
      print("Node.js 版本低于 18。请更新 Node.js ！")
      return False
  except Exception as e:
    print(f"执行 Node.js 版本检查时出错：{e}")
    return False

  try:
    git_version_output = subprocess.run(["git", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    git_version = git_version_output.stdout.strip()
    print(f"Git 版本: {git_version}  √")
  except Exception as e:
    print(f"执行 Git 版本检查时出错：{e}")
    return False
  # print("""    """)
  print(""" 
 ______    ______     ______     ______    
/\__  _\  /\  == \   /\  ___\   /\  ___\   
\/_/\ \/  \ \  __<   \ \___  \  \ \___  \  
   \ \_\   \ \_\ \_\  \/\_____\  \/\_____\ 
    \/_/    \/_/ /_/   \/_____/   \/_____/                                                                                                                                                   
          """)
  return True

def execute_custom_command(command=None):
    init(autoreset=True)
    original_cwd = os.getcwd()  # 保存当前工作目录
    directories = ["Yunzai-Bot", "Yunzai"]
    root_dir = next((d for d in directories if os.path.isdir(d)), None)
    
    if root_dir:
        os.chdir(root_dir)
        if command:
            run_command(command)
        else:
            print("请输入命令(输入0退出)：")
            while True:
                command = input()
                if command == "0":
                    print(Fore.GREEN + "退出自定义指令状态。")
                    os.chdir(original_cwd)  # 返回原始目录
                    break
                print(Fore.GREEN + f"正在执行: {command}")
                try:
                    subprocess.run(command, shell=True, check=True)
                except subprocess.CalledProcessError as e:
                    print(Fore.RED + f"执行命令出错：{e}")
                else:
                    print(Fore.GREEN + "执行完成！(输入0退出)")
        os.chdir(original_cwd)  # 确保切换回原始工作目录
    else:
        print("未找到云崽根目录。请确保 Yunzai-Bot 或 Yunzai 目录存在。")

def download_trss_js_from_git(repo_url, temp_dir, target_filename):
    """使用 Git 从仓库中下载单个文件。"""
    subprocess.run(["git", "clone", repo_url, temp_dir], check=True)
    src_path = path.join(temp_dir, target_filename)
    if os.path.exists(src_path):
        return src_path
    else:
        return None

def is_miao_project(project_dir):
    """判断给定目录的项目是否为 Miao 崽项目。"""
    package_json_path = path.join(project_dir, 'package.json')
    if os.path.exists(package_json_path):
        with open(package_json_path, 'r', encoding='utf-8') as f:
            package_data = json.load(f)
            project_name = package_data.get('name', '')
            return 'miao' in project_name
    return False

def migrate_from_miao_to_trss():
    # 在当前目录下查找 Yunzai-Bot 或 Yunzai 目录
    root_dir = "Yunzai-Bot" if os.path.isdir("Yunzai-Bot") else "Yunzai" if os.path.isdir("Yunzai") else None
    if root_dir and is_miao_project(root_dir):
        os.chdir(root_dir)  # 切换到云崽根目录
        trss_js_path = 'trss.js'

        # 检查 trss.js 文件
        if not os.path.exists(trss_js_path):
            # 临时目录用于克隆仓库
            with tempfile.TemporaryDirectory() as temp_dir:
                print("未找到 trss.js，开始从远程仓库下载...")
                repo_url = "https://gitee.com/yoimiya-kokomi/Miao-Yunzai.git"
                src_path = download_trss_js_from_git(repo_url, temp_dir, 'trss.js')
                if src_path:
                    shutil.copy(src_path, trss_js_path)
                    print("下载 trss.js 成功。")
                else:
                    print("下载 trss.js 失败。")

        # 执行迁移脚本
        subprocess.run(["node", trss_js_path], check=True)
        print("迁移成功！")
        os.chdir("..")  # 返回到上一级目录
    else:
        print("当前不是Miao崽！暂不支持该选项操作！")


def run_command(command, ignore_errors=False):
    # 初始化colorama
    init(autoreset=True)
    print(Fore.GREEN + f"正在执行: {command}")
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        if not ignore_errors:
            print(Fore.RED + f"执行命令出错：{e}")
        return False

def git_clone_redis():
    run_command("git clone --depth 1 https://gitee.com/bling_yshs/redis-windows-7.0.4")

def git_clone_trss():
    run_command("git clone --depth 1 https://gitee.com/TimeRainStarSky/Yunzai")

def install_plugins():
    if os.path.isdir("Yunzai") or os.path.isdir("Yunzai-Bot"):
        #os.chdir("Yunzai" if os.path.isdir("Yunzai") else "Yunzai-Bot")
        execute_custom_command("git clone --depth 1 https://Yunzai.TRSS.me plugins/TRSS-Plugin")
        execute_custom_command("git clone --depth 1 https://gitee.com/TimeRainStarSky/Yunzai-genshin plugins/genshin")
        execute_custom_command("git clone --depth 1 https://gitee.com/yoimiya-kokomi/miao-plugin plugins/miao-plugin")
        #run_command("git clone --depth 1 https://Yunzai.TRSS.me plugins/TRSS-Plugin")
        #run_command("git clone --depth 1 https://gitee.com/TimeRainStarSky/Yunzai-genshin plugins/genshin")
        #run_command("git clone --depth 1 https://gitee.com/yoimiya-kokomi/miao-plugin plugins/miao-plugin")
        #os.chdir("..")
    else:
        print("未找到Yunzai或Yunzai-Bot目录。请先执行Git Clone项目操作。")

def start_trss():
    if os.path.isdir("Yunzai") or os.path.isdir("Yunzai-Bot"):
        execute_custom_command("node .")
        #os.chdir("Yunzai" if os.path.isdir("Yunzai") else "Yunzai-Bot")
        #run_command("node .")
        #os.chdir("..")
    else:
        print("未找到Yunzai或Yunzai-Bot目录。请先执行Git Clone项目操作。")

def install_pnpm_and_dependencies():
    run_command("npm i -g pnpm --registry=https://registry.npmmirror.com")
    if os.path.isdir("Yunzai") or os.path.isdir("Yunzai-Bot"):
        execute_custom_command("pnpm i --registry=https://registry.npmmirror.com")
        #os.chdir("Yunzai" if os.path.isdir("Yunzai") else "Yunzai-Bot")
        #run_command("pnpm i --registry=https://registry.npmmirror.com")
        #os.chdir("..")
    else:
        print("未找到Yunzai或Yunzai-Bot目录。请先执行Git Clone项目操作。")

def is_port_in_use(port):
    # 检查端口是否被占用
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def start_redis_windows():
    redis_folder = next((f for f in os.listdir('.') if f.startswith('redis-windows')), None)
    if redis_folder:
        os.chdir(redis_folder)

        # 读取redis.conf文件
        config_file = "redis.conf"
        bind = "127.0.0.1"
        port = 6379  # 默认端口

        if os.path.exists(config_file):
            with open(config_file, 'r') as file:
                for line in file:
                    if line.startswith("bind"):
                        bind = line.split()[1]
                    elif line.startswith("port"):
                        port = int(line.split()[1])

        # 检查端口是否被占用
        if is_port_in_use(port):
            print(Fore.RED + "当前端口 {port} 已被占用！可能已有redis服务正在运行！")            
        else:
            # 运行启动命令
            run_command("start 双击我启动redis.bat")

        os.chdir("..")
    else:
        print("未找到redis-windows文件夹。请确保已经执行了相应的Git Clone操作。")

def stop_all_redis_windows():
    redis_folder = next((f for f in os.listdir('.') if f.startswith('redis-windows')), None)
    if redis_folder:
        os.chdir(redis_folder)
        run_command("taskkill /IM redis-server.exe /F", ignore_errors=True)
        os.chdir("..")
    else:
        print("未找到redis-windows文件夹。请确保已经执行了相应的Git Clone操作。")


def stop_redis_windows():
    redis_folder = next((f for f in os.listdir('.') if f.startswith('redis-windows')), None)
    if redis_folder:
        os.chdir(redis_folder)
        redis_path = os.path.abspath("redis-server.exe")
        
        # 查找并终止特定路径的redis-server.exe进程
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            if proc.info['name'] == 'redis-server.exe' and proc.info['exe'] == redis_path:
                try:
                    proc.terminate()
                    proc.wait(timeout=5)  # 等待进程终止
                    print(f"成功终止进程: {proc.info['pid']}")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired) as e:
                    print(f"无法终止进程 {proc.info['pid']}: {e}")

        os.chdir("..")
    else:
        print("未找到redis-windows文件夹。请确保已经执行了相应的Git Clone操作。")



def display_menu():
    print("""
当前版本: v0.1.5
===TRSS安装===
1.--获取redis-windows-7.0.4
2.--Git Clone TRSS
3.--安装插件(TRSS+Genshin+Miao)
4.--安装 pnpm 和 依赖
5.--启动 redis-windows
6.--启动 TRSS
7.**自定义终端命令**
8.**关闭所有redis-server.exe的进程**
9.**从Miao云崽迁移至TRSS云崽**
0. 退出程序
          """)
    choice = input("\n请选择操作：")
    return choice

def main():
    # 初始化colorama
    init(autoreset=True)
    if not check_environment():
        print(Fore.GREEN + "按下任意键退出...")
        input()
        return
    while True:
        choice = display_menu()
        if choice == "1":
            git_clone_redis()
        elif choice == "2":
            git_clone_trss()
        elif choice == "3":
            install_plugins()
        elif choice == "4":
            install_pnpm_and_dependencies()
        elif choice == "5":
            start_redis_windows()
        elif choice == "6":
            start_trss()
        elif choice == "7":
            execute_custom_command()
        elif choice == "8":
            stop_all_redis_windows()
        elif choice == "9":
            migrate_from_miao_to_trss()
        elif choice == "0":
            # 在退出时，先关闭TRSS服务，再关闭 redis-windows 服务
            execute_custom_command("node . stop")
            stop_redis_windows() 
            break
        else:
            print(Fore.RED + "无效的选择，请重新输入。")
        print(Fore.GREEN + "操作完成，按下任意键继续...")
        input()

if __name__ == "__main__":
    main()


