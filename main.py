from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import pandas as pd

driver = webdriver.Chrome()

def test_eight_components(sn):
    driver.get("https://www.dell.com/support/home/ja-jp/product-support/servicetag/" + sn + "/overview")

    # 创建一个空的数据框来存储结果
    data = []

    driver.implicitly_wait(0.5)
    time.sleep(30)

    # 抓取到期时间
    try:
        expiryDate = driver.find_element(by=By.CLASS_NAME, value="warrantyExpiringLabel")
        expiryDate = expiryDate.text
        print(expiryDate)
    except NoSuchElementException:
        expiryDate = '-'
        print("未找到元素，跳过")


    # 点击后展示的内容
    # 点击事件
    clickBtn = driver.find_element(by=By.ID, value="viewDetailsWarranty")
    clickBtn.click()

    # 抓取位置
    try:
        locationContent = driver.find_element(By.CSS_SELECTOR, "#countryLabel div")
        locationContent = locationContent.text
        print(locationContent)
    except NoSuchElementException:
        locationContent = '-'
        print("未找到元素，跳过")

    # 抓取 エクスプレス サービス コード
    try:
        expiryCode = driver.find_element(By.CSS_SELECTOR, "#expressservicelabel div")
        expiryCode = expiryCode.text
        print(expiryCode)
    except NoSuchElementException:
        expiryCode = '-'
        print("未找到元素，跳过")

    # 抓取 出荷日
    try:
        shippingDate = driver.find_element(By.CSS_SELECTOR, "#shippingDateLabel div")
        shippingDate = shippingDate.text
        print(shippingDate)
    except NoSuchElementException:
        shippingDate = '-'
        print("未找到元素，跳过")

    # 抓取 サポート サービス:
    try:
        suppSvcPlan = driver.find_element(By.CSS_SELECTOR, "#supp-svc-plan-txt-1 span")
        suppSvcPlan = suppSvcPlan.text
        print(suppSvcPlan)
    except NoSuchElementException:
        suppSvcPlan = '-'
        print("未找到元素，跳过")

    # 抓取 サービス タグ:
    try:
        serviceTag = driver.find_element(By.CSS_SELECTOR, "#serviceTagLabel div")
        serviceTag = serviceTag.text
        print(serviceTag)
    except NoSuchElementException:
        serviceTag = '-'
        print("未找到元素，跳过")

    # 抓取型号
    try:
        serverType = driver.find_element(by=By.CLASS_NAME, value="desc-size")
        serverType = serverType.text
        print(serverType)
    except NoSuchElementException:
        serverType = -''
        print("未找到元素，跳过")

    time.sleep(5)

    # 将结果添加到数据框
    data.append([expiryDate, locationContent, expiryCode, shippingDate, suppSvcPlan, serviceTag, serverType])
    # 创建一个 pandas 数据框
    df = pd.DataFrame(data, columns=["到期时间", "位置", "エクスプレス サービス コード", "出荷日", "サポート サービス", "サービス タグ", "型号"])

    # 打印表格形式的结果
    print(df)
    # 导出为CSV文件（追加）
    df.to_csv("server_data.csv", mode='a', header=False, index=False)
    # 下面是覆盖
    # df.to_csv("server_data.csv", index=False)
    # print("Data exported to server_data.csv")

def read_txt_file(file_path):
    try:
        # 打开文件并指定只读模式 ('r')
        with open(file_path, 'r') as file:
            # 或者逐行读取文件内容并保存为列表
            content_list = file.readlines()
        # 返回文件内容（整个内容或行列表）
        return content_list
    except FileNotFoundError:
        print(f"文件 '{file_path}' 未找到。")
        return None


if __name__ == '__main__':

    # 示例：读取 example.txt 文件内容
    file_path = 'sn_list.txt'
    sn_list = []

    file_content = read_txt_file(file_path)
    if file_content is not None:
        # 打印文件内容
        for line in file_content:
            sn_list.append(line.strip())
            # print(array_data)

    for sn in sn_list:
        test_eight_components(sn)

    driver.quit()
    print("Data exported to server_data.csv")