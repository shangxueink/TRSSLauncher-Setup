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
        node_version_output = subprocess.run(["node", "-v"],
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE,
                                             text=True)
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
        git_version_output = subprocess.run(["git", "--version"],
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            text=True)
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


def execute_custom_command(command=None, new_window=False):
    init(autoreset=True)
    original_cwd = os.getcwd()  # 保存当前工作目录
    directories = ["Yunzai-Bot", "Yunzai"]
    root_dir = next((d for d in directories if os.path.isdir(d)), None)

    if root_dir:
        os.chdir(root_dir)
        if command:
            if new_window:
                subprocess.Popen(f'start cmd /k {command}', shell=True)
            else:
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
                    if new_window:
                        subprocess.Popen(f'start cmd /k {command}', shell=True)
                    else:
                        run_command(command)
                except subprocess.CalledProcessError as e:
                    print(Fore.RED + f"执行命令出错：{e}")
                else:
                    print(Fore.GREEN + "执行完成！(输入0退出)")
        os.chdir(original_cwd)  # 确保切换回原始工作目录
    else:
        print("未找到云崽根目录。请确保 Yunzai-Bot 或 Yunzai 目录存在。")


def start_trss():
    execute_custom_command("node .", new_window=True)


def del_and_reinstall_dependencies():
    init(autoreset=True)
    original_cwd = os.getcwd()  # 保存当前工作目录
    # print(Fore.BLUE + f"当前工作目录: {original_cwd}")

    directories = ["Yunzai-Bot", "Yunzai"]
    root_dir = next((d for d in directories if os.path.isdir(d)), None)
    # print(Fore.BLUE + f"检测到的目录: {directories}")

    if root_dir:
        #print(Fore.GREEN + f"找到目录: {root_dir}")
        node_modules_path = os.path.join(root_dir, "node_modules")
        if os.path.isdir(node_modules_path):
            choice = input(Fore.RED + "检测到node_modules文件夹，是否覆盖？(y/n): ")
            if choice.lower() == "y":
                print(Fore.YELLOW + "正在删除node_modules...")
                shutil.rmtree(node_modules_path)
                print(Fore.GREEN + "node_modules 文件夹已删除。")
            else:
                print(Fore.YELLOW + "操作取消。")
                return
        os.chdir(root_dir)
        #print(Fore.GREEN + f"切换到目录: {root_dir}")

        # 确认切换后的工作目录
        # current_cwd = os.getcwd()
        # print(Fore.BLUE + f"当前工作目录: {current_cwd}")

        os.chdir(original_cwd)
        execute_custom_command(
            "pnpm i --registry=https://registry.npmmirror.com")
    else:
        print(Fore.RED + "未找到云崽根目录。请确保 Yunzai-Bot 或 Yunzai 目录存在。")


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
    root_dir = "Yunzai-Bot" if os.path.isdir(
        "Yunzai-Bot") else "Yunzai" if os.path.isdir("Yunzai") else None
    if root_dir and is_miao_project(root_dir):
        os.chdir(root_dir)  # 切换到云崽根目录
        trss_js_path = 'trss.js'

        # 检查 trss.js 文件
        if not os.path.exists(trss_js_path):
            # 临时目录用于克隆仓库
            with tempfile.TemporaryDirectory() as temp_dir:
                print("未找到 trss.js，开始从远程仓库下载...")
                repo_url = "https://gitee.com/yoimiya-kokomi/Miao-Yunzai.git"
                src_path = download_trss_js_from_git(repo_url, temp_dir,
                                                     'trss.js')
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


def git_clone(repository_url, target_folder):
    # 检查目标文件夹是否存在
    if os.path.exists(target_folder):
        if os.path.isdir(target_folder) and os.listdir(target_folder):
            # 如果文件夹不为空，询问用户是否覆盖
            answer = input(
                Fore.RED +
                f"文件夹 {target_folder} 已存在且不为空。是否覆盖? (y/n): ").lower()
            if answer != 'y':
                print(Fore.GREEN + f"已跳过克隆操作。")
                return
            else:
                # 如果用户选择覆盖，先删除现有文件夹
                shutil.rmtree(target_folder)
        else:
            # 如果目标存在但不是文件夹，则删除
            os.remove(target_folder)

    # 执行 git clone 命令
    run_command(f"git clone --depth 1 {repository_url} {target_folder}")


def git_clone_redis():
    git_clone("https://gitee.com/bling_yshs/redis-windows-7.0.4",
              "redis-windows-7.0.4")


def git_clone_trss():
    git_clone("https://gitee.com/TimeRainStarSky/Yunzai", "Yunzai")


def install_plugins():
    execute_custom_command(
        "git clone --depth 1 https://gitee.com/TimeRainStarSky/TRSS-Plugin/ plugins/TRSS-Plugin"
    )
    execute_custom_command(
        "git clone --depth 1 https://gitee.com/TimeRainStarSky/Yunzai-genshin plugins/genshin"
    )
    execute_custom_command(
        "git clone --depth 1 https://github.com/yoimiya-kokomi/miao-plugin plugins/miao-plugin"
    )


def install_pnpm_and_dependencies():
    run_command("npm i -g pnpm --registry=https://registry.npmmirror.com")
    execute_custom_command("pnpm i --registry=https://registry.npmmirror.com")


def is_port_in_use(port):
    # 检查端口是否被占用
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


def start_redis_windows():
    redis_folder = next(
        (f for f in os.listdir('.') if f.startswith('redis-windows')), None)
    if redis_folder:
        os.chdir(redis_folder)
        # 读取redis.conf文件
        config_file = "redis.conf"
        if os.path.exists(config_file):
            # 检查端口是否被占用
            with open(config_file, 'r') as file:
                for line in file:
                    if line.startswith("bind"):
                        bind = line.split()[1]
                    elif line.startswith("port"):
                        port = int(line.split()[1])

            if is_port_in_use(port):
                print(Fore.RED + f"当前端口 {port} 已被占用！可能已有redis服务正在运行！")
            else:
                # 运行启动命令
                # 使用 Popen 在新的命令提示符窗口中运行 redis-server.exe redis.conf
                subprocess.Popen(["redis-server.exe", "redis.conf"],
                                 creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            print("未找到 redis.conf 文件。")
        os.chdir("..")
    else:
        print("未找到redis-windows文件夹。请确保已经执行了相应的Git Clone操作。")


def stop_all_redis_windows():
    redis_folder = next(
        (f for f in os.listdir('.') if f.startswith('redis-windows')), None)
    if redis_folder:
        os.chdir(redis_folder)
        run_command("taskkill /IM redis-server.exe /F", ignore_errors=True)
        os.chdir("..")
    else:
        print("未找到redis-windows文件夹。请确保已经执行了相应的Git Clone操作。")


def stop_all_nodejs():
    node_processes = "node.exe"
    run_command(f"taskkill /IM {node_processes} /F", ignore_errors=True)
    print("所有 Node.js 进程已关闭。")


def stop_redis_windows():
    redis_folder = next(
        (f for f in os.listdir('.') if f.startswith('redis-windows')), None)
    if redis_folder:
        os.chdir(redis_folder)
        redis_path = os.path.abspath("redis-server.exe")

        # 查找并终止特定路径的redis-server.exe进程
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            if proc.info['name'] == 'redis-server.exe' and proc.info[
                    'exe'] == redis_path:
                try:
                    proc.terminate()
                    proc.wait(timeout=5)  # 等待进程终止
                    print(f"成功终止进程: {proc.info['pid']}")
                except (psutil.NoSuchProcess, psutil.AccessDenied,
                        psutil.TimeoutExpired) as e:
                    print(f"无法终止进程 {proc.info['pid']}: {e}")

        os.chdir("..")
    else:
        print("未找到redis-windows文件夹。请确保已经执行了相应的Git Clone操作。")


def display_main_menu():
    print("""
当前版本: v0.1.6
===TRSS管理===
1. 安装 TRSS 云崽
2. 管理 TRSS 云崽
3. TRSS 云崽工具
-1. 退出本程序
""")
    choice = input(Fore.YELLOW + "\n请选择操作：")
    print(Fore.RESET)  # 重置颜色
    return choice


def display_1_menu():
    print("""
===安装 TRSS 云崽===
1. 获取 redis-windows-7.0.4
2. 获取 TRSS 云崽
3. 安装插件( TRSS + Genshin + Miao )
4. 安装 pnpm 和 插件依赖
5. 启动 redis-windows 服务
6. 启动 TRSS 云崽
0. 返回上一级
""")
    choice = input(Fore.YELLOW + "\n请选择操作：")
    print(Fore.RESET)  # 重置颜色
    return choice


def display_2_menu():
    print("""
===管理 TRSS 云崽===
1. 启动 redis-windows-7.0.4 服务
2. 启动 TRSS 云崽
3. 自定义 TRSS 终端命令
4. 安装依赖
5. **关闭 redis 和 TRSS 云崽**
6. **关闭所有 redis-server.exe 的进程**
7. **关闭所有 nodejs 的进程**
0. 返回上一级
""")
    choice = input(Fore.YELLOW + "\n请选择操作：")
    print(Fore.RESET)  # 重置颜色
    return choice


def display_3_menu():
    print("""
===TRSS 云崽工具===
1. 从 Miao 云崽迁移至 TRSS 云崽
2. 重装 TRSS 的依赖
0. 返回上一级
""")
    choice = input(Fore.YELLOW + "\n请选择操作：")
    print(Fore.RESET)  # 重置颜色
    return choice


def main():
    # 初始化 colorama
    init(autoreset=True)

    if not check_environment():
        print(Fore.GREEN + "按下任意键退出...")
        input()
        return

    while True:
        choice = display_main_menu()
        if choice == "1":
            while True:
                choice = display_1_menu()
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
                elif choice == "0":
                    break
                else:
                    print(Fore.RED + "无效的选择，请重新输入。")
        elif choice == "2":
            while True:
                choice = display_2_menu()
                if choice == "1":
                    start_redis_windows()
                elif choice == "2":
                    start_trss()
                elif choice == "3":
                    execute_custom_command()
                elif choice == "4":
                    install_pnpm_and_dependencies()
                elif choice == "5":
                    # 先关闭 TRSS 服务，再关闭 redis-windows 服务
                    execute_custom_command("node . stop")
                    stop_redis_windows()
                elif choice == "6":
                    stop_all_redis_windows()
                elif choice == "7":
                    stop_all_nodejs()
                elif choice == "0":
                    break
                else:
                    print(Fore.RED + "无效的选择，请重新输入。")
        elif choice == "3":
            while True:
                choice = display_3_menu()
                if choice == "1":
                    migrate_from_miao_to_trss()
                elif choice == "2":
                    del_and_reinstall_dependencies()
                elif choice == "0":
                    break
                else:
                    print(Fore.RED + "无效的选择，请重新输入。")
        elif choice == "-1":
            break
        else:
            print(Fore.RED + "无效的选择，请重新输入。")
        print(Fore.GREEN + "操作完成，按下任意键继续...")
        input()


if __name__ == "__main__":
    main()
