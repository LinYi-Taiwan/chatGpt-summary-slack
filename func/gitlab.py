import requests
import os
import pandas as pd
from dotenv import load_dotenv


env_path = '.env'
load_dotenv(dotenv_path=env_path)
gitlab_token = os.environ['GITLAB_ACCESS_TOKEN']
domain = os.environ['GITLAB_DOMAIN']


class Gitlab(object):
    def __init__(self):
        super(Gitlab, self).__init__()
        self.token = gitlab_token
        self.starred_project = self.request_starred_project()

        # todo: 驗證 token 是否正確，若不正確則...

        # if self._check_input_exist_in_starred_list(project_name):
        #     self.project_name = project_name
        #     self.project_id = self.get_project_id()
        #     self.project_issues = pd.DataFrame(self.get_project_all_issues())

    # 取得指定 project id 的 issue list
    # query string:
    # state -> issue 的開啟狀態，目前預設開啟
    # labels -> issue 的標籤，目前預設 Web （需要與 pm 協作定義）
    def get_project_all_issues(self, project_name):
        issue_frames = []

        headers = {"Authorization": "Bearer {}".format(self.token)}

        project_id = self.get_project_id(project_name)

        res = requests.get(
            "{}/api/v4/projects/{}/issues?page=1&per_page=100".format(domain,
                                                                      project_id
                                                                      ),
            headers=headers,
        )

        issue_frames.append(pd.DataFrame(res.json()))
        total_pages = int(res.headers['X-Total-Pages'])
        if total_pages > 1:
            for page in range(2, total_pages+1):
                issues = requests.get(
                    "{}/api/v4/projects/{}/issues?page={}&per_page=100".format(domain,
                                                                               project_id, page
                                                                               ),
                    headers=headers,
                )
                issue_frames.append(pd.DataFrame(issues.json()))

        return pd.concat(issue_frames)

    # 取得訂閱的專案清單
    def request_starred_project(self):
        headers = {"Authorization": "Bearer {}".format(self.token)}
        res = requests.get(
            "{}/api/v4/users/424/starred_projects".format(domain),
            headers=headers,
        )
        df = pd.DataFrame(res.json())

        # 抽取專案 id 與名稱
        df = df[["id", "namespace"]]
        df["namespace"] = df["namespace"].map(
            lambda x: x["name"] if x != None else "Anonymous"
        )

        return df

    # 根據訂閱的專案清單，取得輸入專案的 id
    def get_project_id(self, project_name):
        project_id = self.starred_project[
            self.starred_project["namespace"] == project_name
        ].id.values[0]
        return project_id

    # 獲得正在追蹤的成員資訊
    def get_following_member(self):
        headers = {"Authorization": "Bearer {}".format(self.token)}
        res = requests.get(
            "{}/api/v4/users/424/following".format(domain), headers=headers
        )

        df = pd.DataFrame(res.json())

        return df

    # 獲得正在追蹤的成員資訊目前的 issue
    def get_following_member_issues(self, member_id):
        headers = {"Authorization": "Bearer {}".format(self.token)}
        res = requests.get(
            "{}/api/v4/issues?assignee_id={}&scope=all&state=opened".format(domain,
                                                                            member_id
                                                                            ),
            headers=headers,
        )

        df = pd.DataFrame(res.json())

        return df

    def get_assignee(self):
        normalize_data = pd.json_normalize(self.project_issues.assignee)
        return pd.DataFrame(normalize_data)

    # 此為裝飾器，負責判斷 project_issues 是否為空，若為空則回傳 400
    def _check_dataframe_is_empty(func):
        def wrapper(self, data):
            if data.empty:
                print("{} issues list is empty.".format(self.project_name))
                return {"status": 400, "msg": "List is empty.", "data": []}
            else:
                return func(self, data)

        return wrapper

    # 產生畫圖的資料結構，並在執行前先確認是否資料為空
    @_check_dataframe_is_empty
    def generate_timeline_graph_data(self, data):
        # 只拿 issue title & due_date ，並重命名 fit 畫 timeline 格式
        format_df = data[["title", "due_date", "assignee"]].rename(
            {"title": "Task", "due_date": "End"}, axis=1
        )

        # 將 assignee obj 抽取出來
        format_df["assignee"] = format_df["assignee"].map(
            lambda x: x["name"] if x != None else ""
        )

        # 只拿 due_date != 空值的 row
        format_df = format_df[format_df["End"].notnull()]
        format_df["End"] = format_df["End"].apply(pd.to_datetime)

        format_df["Completed"] = 1
        return {"status": 200, "data": format_df}

    # 驗證輸入的資料非空，且存在在訂閱的專案清單中
    def _check_input_exist_in_starred_list(self, input_project_name):
        return (
            len(str(input_project_name)) != 0
            and not self.starred_project[
                self.starred_project["namespace"].str.contains(
                    input_project_name)
            ].empty
        )
