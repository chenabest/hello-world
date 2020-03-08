# Owner: <achen>
# !/usr/bin/python3
# 2020/2/25 11:17 PM
# mouse_and_keyboard_controller

from appium_robot.robot.tools.function_tools import *
from appium_robot.robot.tools.appium_functools import get_all_online_serials
from pynput import keyboard, mouse
import json

m_controller = mouse.Controller()
m_button = mouse.Button

k_controller = keyboard.Controller()
k_key = keyboard.Key

DELAY = 1


"""
神技能：Python控制键盘鼠标 https://www.jianshu.com/p/48e3579d3073
"""


def click(position=None, times=1):
    time.sleep(DELAY)
    if position:
        global m_controller
        m_controller.position = position
    for i in range(times):
        m_controller.press(m_button.left)
        m_controller.release(m_button.left)
        time.sleep(0.01)


def get_mouse_position():
    return m_controller.position


def mouse_listener():
    pass


def send_keys_and_press_enter(keys_to_send: str):
    """
    操作键盘，输入字母和数字
    :param keys_to_send: 必须是字母和数字构成的字符串
    :return: None
    """
    time.sleep(DELAY)
    k_controller.type(keys_to_send)
    k_controller.press(k_key.enter)


def keyboard_listener():
    pass


def copy():
    time.sleep(DELAY)
    k_controller.press(k_key.cmd)
    k_controller.press('a')
    k_controller.release('a')
    k_controller.press('c')
    k_controller.release('c')
    k_controller.release(k_key.cmd)


def paste():
    time.sleep(DELAY)
    k_controller.press(k_key.cmd)
    k_controller.press('v')
    k_controller.release('v')
    k_controller.release(k_key.cmd)


def paste_to_file(file_name, dir_path=None):
    time.sleep(DELAY)
    if dir_path:
        send_keys_and_press_enter('cd '+dir_path)
    send_keys_and_press_enter(f'vim {file_name}')
    time.sleep(1.5)
    k_controller.type('i')
    paste()
    k_controller.press(k_key.esc)
    k_controller.release(k_key.esc)
    time.sleep(1)
    send_keys_and_press_enter(':wq')
    time.sleep(1.5)
    if dir_path:
        send_keys_and_press_enter('cd -')


def clear_screen():
    time.sleep(DELAY)
    k_controller.press(k_key.cmd)
    k_controller.press('k')
    k_controller.release('k')
    k_controller.release(k_key.cmd)


def get_serial_uin_from_file(file_name='wechat_auth_key_all.txt',
                             dir_path='/Users/achen/workspaces/data_automation'):
    with open(os.path.join(dir_path, file_name), 'r') as f:
        text = f.read()
    serials_list = re.findall('adb -s (\S+)\s+shell.*?name="_auth_uin"\s*value="(\S+)"', text, re.DOTALL)
    serial_uid_dict = {}
    for item in serials_list:
        serial_uid_dict[item[0]] = item[1]
    return serial_uid_dict


def save_to_json(data, file_name='wechat_auth_key_all.json',
                 dir_path='/Users/achen/workspaces/data_automation'):
    file_path = os.path.join(dir_path,file_name)
    with open(file_path, 'w+') as f:
        json.dump(data, f, ensure_ascii=False)
    print(f"POSITION_DICT写入json文件：{file_path}  ok")


def main():
    print('请在15秒内，完成操作：切换输入法为英文，打开terminal，并移动鼠标到terminal主界面...')
    time.sleep(15)
    position = get_mouse_position()
    print(position)
    click(position=position, times=1)
    clear_screen()
    serials = get_all_online_serials()
    pprint(serials)
    for serial in serials:
        send_keys_and_press_enter(f'adb -s {serial} shell')
        time.sleep(1)
        send_keys_and_press_enter('su')
        time.sleep(1)
        send_keys_and_press_enter('cd /data/data/com.tencent.mm/shared_prefs/')
        send_keys_and_press_enter('cat auth_info_key_prefs.xml | grep _auth_key')
        send_keys_and_press_enter('exit')
        send_keys_and_press_enter('exit')
        time.sleep(1)
    copy()
    click(position=position, times=1)
    paste_to_file('wechat_auth_key_all.txt', dir_path='/Users/achen/workspaces/data_automation')
    serial_uid_dict = get_serial_uin_from_file()
    pprint(serial_uid_dict)
    save_to_json(serial_uid_dict)

if __name__ == '__main__':
    show_module(form='*')
