import requests
import datetime
import os


# ===================== 初始化存储目录/文件 =====================
def init_storage():
    """初始化待办和笔记的存储目录，避免文件不存在报错"""
    # 待办文件直接在当前目录创建
    if not os.path.exists("todo.txt"):
        with open("todo.txt", "w", encoding="utf-8") as f:
            f.write("")  # 创建空待办文件
    # 笔记目录
    if not os.path.exists("notes"):
        os.makedirs("notes")  # 创建笔记文件夹


# ===================== 待办事项管理功能 =====================
def add_todo():
    """添加待办事项"""
    todo_content = input("请输入待办事项内容：").strip()
    if not todo_content:
        print("待办事项内容不能为空！")
        return
    # 记录创建时间
    create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 追加写入待办文件
    with open("todo.txt", "a", encoding="utf-8") as f:
        f.write(f"[{create_time}] {todo_content}\n")
    print(f"待办事项「{todo_content}」添加成功！")


def view_todo():
    """查看所有待办事项"""
    with open("todo.txt", "r", encoding="utf-8") as f:
        todos = f.readlines()
    if not todos:
        print("当前暂无待办事项！")
        return
    print("=" * 20 + " 我的待办 " + "=" * 20)
    for idx, todo in enumerate(todos, start=1):
        print(f"{idx}. {todo.strip()}")
    print("=" * 50)


def delete_todo():
    """删除指定序号的待办事项"""
    view_todo()  # 先展示所有待办
    with open("todo.txt", "r", encoding="utf-8") as f:
        todos = f.readlines()
    if not todos:
        return
    try:
        del_idx = int(input("请输入要删除的待办事项序号：")) - 1
        if del_idx < 0 or del_idx >= len(todos):
            print("无效的序号！")
            return
        del_todo = todos[del_idx].strip()
        # 重新写入剩余待办
        with open("todo.txt", "w", encoding="utf-8") as f:
            f.write("".join([todo for idx, todo in enumerate(todos) if idx != del_idx]))
        print(f"待办事项「{del_todo}」删除成功！")
    except ValueError:
        print("请输入有效的数字序号！")


# ===================== 天气查询功能（已填入你的高德Key，立即可用） =====================
def get_weather():
    """查询指定城市的实时天气（高德服务端API，已配置你的Key）"""
    # 已填入你提供的高德服务端API Key
    GAODE_API_KEY = "7047c3e40a4119a5b664ea7df7dd4b45"
    if GAODE_API_KEY.strip() == "":
        print("请先配置有效的高德服务端API Key！")
        return
    city = input("请输入要查询的城市名称（如：北京、上海）：").strip()
    if not city:
        print("城市名称不能为空！")
        return

    # 高德服务端天气接口（与服务端Key匹配，稳定可用）
    weather_url = f"https://restapi.amap.com/v3/weather/weatherInfo?city={city}&key={GAODE_API_KEY}&extensions=base"
    try:
        response = requests.get(weather_url, timeout=15)
        # 调试信息
        print(f"【调试信息】高德天气接口状态码：{response.status_code}")
        print(f"【调试信息】高德天气接口返回内容：{response.text}")

        if response.status_code != 200:
            print(f"天气查询失败：接口请求失败，状态码：{response.status_code}")
            return

        # JSON解析兜底
        try:
            weather_data = response.json()
        except Exception as json_err:
            print(f"JSON解析失败：{json_err}，接口返回非JSON内容：{response.text}")
            return

        # 校验高德接口业务状态
        if weather_data["status"] != "1":
            err_info = weather_data.get("info", "未知错误")
            err_code = weather_data.get("infocode", "未知错误码")
            print(f"天气查询失败！错误信息：{err_info}，错误码：{err_code}")
            # 针对性提示Key平台不匹配问题
            if err_info == "USERKEY_PLAT_NOMATCH":
                print("解决方案：请确认你的Key是「服务端」类型，若不是请重新申请！")
            return

        # 校验是否有天气数据
        if not weather_data.get("lives"):
            print(f"未查询到城市「{city}」的天气信息！请确认城市名称正确（如：北京、上海）。")
            return

        # 解析天气数据
        live_weather = weather_data["lives"][0]
        city_name = live_weather["city"]
        temp = live_weather["temperature"]
        weather_text = live_weather["weather"]
        wind_dir = live_weather["winddirection"]
        wind_sc = live_weather["windpower"]
        humidity = live_weather["humidity"]  # 新增湿度信息
        update_time = live_weather["reporttime"]

        # 展示天气信息
        print("=" * 20 + f" {city_name} 实时天气 " + "=" * 20)
        print(f"更新时间：{update_time}")
        print(f"天气状况：{weather_text}")
        print(f"实时温度：{temp}℃")
        print(f"风向风力：{wind_dir} {wind_sc}级")
        print(f"空气湿度：{humidity}%")
        print("=" * 50)
    except requests.exceptions.Timeout:
        print("天气查询失败：网络请求超时，请检查网络连接！")
    except Exception as e:
        print(f"天气查询失败：{e}")
        return


# ===================== 快速笔记功能 =====================
def save_note():
    """保存快速笔记，按日期归档"""
    note_content = input("请输入笔记内容：").strip()
    if not note_content:
        print("笔记内容不能为空！")
        return
    # 按当前日期生成笔记文件名
    today = datetime.datetime.now().strftime("%Y%m%d")
    note_file_path = os.path.join("notes", f"{today}_note.txt")
    # 记录笔记时间
    note_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 追加写入笔记
    with open(note_file_path, "a", encoding="utf-8") as f:
        f.write(f"[{note_time}] {note_content}\n")
    print(f"笔记已保存至：{note_file_path}")


# ===================== 日期倒计时功能 =====================
def countdown():
    """计算当前日期到目标日期的剩余天数"""
    target_date_str = input("请输入目标日期（格式：YYYY-MM-DD，如：2026-01-01）：").strip()
    try:
        # 解析目标日期
        target_date = datetime.datetime.strptime(target_date_str, "%Y-%m-%d").date()
        today = datetime.date.today()
        # 计算天数差
        if target_date < today:
            delta_days = (today - target_date).days
            print(f"目标日期「{target_date_str}」已过去 {delta_days} 天！")
        elif target_date == today:
            print(f"目标日期「{target_date_str}」就是今天！")
        else:
            delta_days = (target_date - today).days
            print(f"距离目标日期「{target_date_str}」还有 {delta_days} 天！")
    except ValueError:
        print("日期格式错误！请严格按照YYYY-MM-DD格式输入！")


# ===================== 主菜单 =====================
def main_menu():
    """主菜单界面"""
    init_storage()  # 程序启动时初始化存储
    while True:
        print("\n" + "=" * 15 + " PyLifeHelper 个人生活小助手 " + "=" * 15)
        print("1. 待办事项管理")
        print("2. 实时天气查询")
        print("3. 快速笔记保存")
        print("4. 日期倒计时计算")
        print("0. 退出程序")
        print("=" * 56)
        choice = input("请输入功能序号：").strip()

        if choice == "1":
            # 待办事项子菜单
            while True:
                print("\n" + "=" * 10 + " 待办事项管理 " + "=" * 10)
                print("a. 添加待办")
                print("b. 查看待办")
                print("c. 删除待办")
                print("d. 返回主菜单")
                todo_choice = input("请输入子功能序号：").strip().lower()
                if todo_choice == "a":
                    add_todo()
                elif todo_choice == "b":
                    view_todo()
                elif todo_choice == "c":
                    delete_todo()
                elif todo_choice == "d":
                    break
                else:
                    print("无效的选择，请重新输入！")
        elif choice == "2":
            get_weather()
        elif choice == "3":
            save_note()
        elif choice == "4":
            countdown()
        elif choice == "0":
            print("感谢使用PyLifeHelper，再见！")
            break
        else:
            print("无效的功能序号，请重新输入！")


if __name__ == "__main__":
    main_menu()