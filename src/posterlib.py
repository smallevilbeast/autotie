#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 smallevilbeast
#
# Author:     smallevilbeast <houshao55@gmail.com>
# Maintainer: smallevilbeast <houshao55@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import urllib
import urllib2
import urlparse
import re
import cookielib
import time
    
import socket    
socket.setdefaulttimeout(40) # 40s

import utils
from multipart  import encode_multipart
from logger import Logger

class TiebaLib(Logger):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        
        # 保存cookie
        cookie_file = utils.get_cookie_file(username)
        cj = cookielib.LWPCookieJar(cookie_file)
        cookie_handler = urllib2.HTTPCookieProcessor(cj)
        opener = urllib2.build_opener(cookie_handler)
        opener.addheaders = [
            ('User-agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.24 ' \
             '(KHTML, like Gecko) Chrome/19.0.1056.0 Safari/535.24'),]
        self.cookiejar = cj
        if os.path.isfile(cookie_file):
            self.cookiejar.load(ignore_discard=True, ignore_expires=True)
        
        self.opener = opener
        self.apidata = dict()
        self.__pickack = ""
        self.user_info = {}
        self.login_verify_code = ""
        
    def check_login(self, stage=0):
        self.apidata = dict()
        req = urllib2.Request("http://tieba.baidu.com/")
        ret = self.opener.open(req)
        ret.read() # Fix
        
        check_data = {"ct" : 486539264, "cm" : 59202, "tn" : "jsonUserInfo",
                "t" : utils.get_random_t()}
        ret = self.api_request("f", extra_data=check_data, encoding="gbk")        
        # self.logdebug("Login check return value: %s", ret)
        
        # 登陆校验成功.
        if ret.has_key("is_login") and ret["is_login"] == 1:
            self.user_info = ret
            self.cookiejar.save()
            self.loginfo("Login check success!")
            return True
            
        # 登陆校验失败(超过两次登陆校验)
        if stage >= 2:
            self.loginfo("Login check failed!")
            return False
        
        req = urllib2.Request('https://passport.baidu.com/v2/api/?login&tpl=mn&time=%d' % utils.timestamp())
        data = self.opener.open(req).read().strip()[1:-1] # remove brackets
        data = eval(data, type('Dummy', (dict,), dict(__getitem__=lambda s,n:n))())
        if int(data["error_no"]) != 0:
            self.logdebug("Login passport error: %s", data)
            return False
        
        param_out = data["param_out"]
        param_in = data["param_in"]
        params = {v : param_out[k.replace("name", "contex")] for k, v in param_out.items() if k.endswith("_name")}
        params.update({v: param_in[k.replace("name", "value")] for k,v in param_in.items() if k.endswith("_name")})
        params["username"] = self.username.decode("utf-8").encode("gbk")
        params["password"] = self.password
        params["safeflg"]  = ""
        params["mem_pass"] = "on"
        if int(params["verifycode"]) == 1 and stage == 1:
            self.loginfo("Login check require verifycode")
            params["verifycode"] = self.get_verify_code()
            
        params['staticpage'] = "http://tieba.baidu.com/tb/v2Jump.html"

        print params
        req = urllib2.Request('https://passport.baidu.com/v2/api/?login',
                              data=urllib.urlencode(params))
        html = self.opener.open(req).read()
        url = re.findall(r"encodeURI\('(.*?)'\)", html)[0]
        self.opener.open(url).read()
        
        # 二次登陆校验
        if stage == 0:
            self.loginfo("Begin second login check..")
        elif stage == 1:    
            self.loginfo("Begin three login check..")
        return self.check_login(stage=stage+1)
    
    def sign_by_name(self, tieba_name):
        # http://tieba.baidu.com/sign/loadmonth?kw=bpython&ie=utf-8
        data = {"ie": "utf-8", "kw" : tieba_name, "tbs" : self.get_common_tbs()}
        try:
            ret_data = self.api_request("sign/add", "POST", extra_data=data)
        except:    
            ret_data = None
            
        # if not ret_data:
        #     self.loginfo(u'%s吧, 签到失败!', tieba_name)
        # elif ret_data["error"] != "":    
        #     self.loginfo(u"%s吧! %s", tieba_name, ret_data["error"])
        # else:    
        #     self.loginfo(u'签到成功! %s吧第 %d 个签到', tieba_name, ret_data['data']['finfo']['current_rank_info']['sign_count'])
        # return ret_data    
        
        tieba_name = tieba_name.decode("utf-8", "ignore")    
        if not ret_data:
            print tieba_name, u"吧, 签到失败!"
        elif ret_data["error"] != "":    
            print tieba_name, ret_data["error"]
        else:    
            print u'签到成功!', tieba_name, u'吧第 %d 个签到' % ret_data['data']['finfo']['current_rank_info']['sign_count']
        
    
    def json_myforum(self):
        ret_data = self.api_request("/f/user/json_myforum")
        return ret_data
    
    def get_forumlist(self):
        ret_data = self.api_request("/i/data/get_forumlist")
        return ret_data["data"]
    
    def get_favorite_tiebas(self):
        req = urllib2.Request('http://wapp.baidu.com/m?tn=bdFBW&tab=favorite')
        page = self.opener.open(req).read()
        ret = re.findall('<a href="/f/[-_\w]+?/m\?kw=[%\w]+?">(.+?)</a>', page)
        if ret:
            return ret
        return []
    
    def get_user_portrait(self):
        url = "http://tb.himg.baidu.com/sys/portrait/item/%s" % self.user_info["user_portrait"]
        return url
        
    def get_common_tbs(self):
        ret = self.api_request("dc/common/tbs")
        return ret["tbs"]
    
    def get_common_imgtbs(self):
        ret = self.api_request("dc/common/imgtbs")
        return ret["data"]["tbs"]
    
    def sign_list(self):
        ret = self.api_request("f/user/sign_list?t=%s" % utils.timechecksum())
        return ret
    
    def get_forum_id(self, tieba_name):
        params = { "kw" : tieba_name, "ie" : "utf-8", "tbs" : self.get_common_tbs, "_" : utils.timestamp}
        ret = self.api_request("sign/info", extra_data=params)
        try:
            return ret["data"]["forum_info"]["forum_info"]["forum_id"]
        except:
            try:
                req = urllib2.Request("http://tieba.baidu.com/f?kw=%s" % tieba_name)
                ret_value = self.opener.open(req).read()
                fid = re.findall("fid:'(\d+)'", ret_value)
                if fid:
                    return fid[0]
            except:    
                return 0
    
    def check_need_vcode(self, tieba_name):
        params = {"rs1": 0, "rs10" : 1, "lm" : self.get_forum_id(tieba_name),
                  "word" : tieba_name, "t" : utils.get_random_t()}
        ret = self.api_request("f/user/json_needvcode", extra_data=params)
        try:
            if ret["data"]["need"] == 1:
                vcode_ret = self.api_request(ret["data"]["vcodeUrl"])
                vcodestr = vcode_ret["data"]["vcodestr"]
                url = "http://tieba.baidu.com/cgi-bin/genimg?%s" % vcodestr
                req = urllib2.Request(url)
                ret_data = self.opener.open(req).read()
                pic_image = utils.get_cache_file("vcode")
                with open(pic_image, "wb") as fp:
                    fp.write(ret_data)
                self.loginfo("Verify code pic download ok! save to %s", pic_image)
                return pic_image, vcodestr
        except Exception, e:    
            self.logdebug("Check newTie verify code faild, error: %s", e)
        return None
    
    def upload_pic(self, image_file):
        fp = open(image_file, "rb")
        image_data = fp.read()
        fp.close()
        img_ext = os.path.splitext(image_file)[1]
        url = "http://upload.tieba.baidu.com/upload/pic"
        pic_url = "http://imgsrc.baidu.com/forum/pic/item/%s%s"
        content_type, body = encode_multipart(
            [("Filename", os.path.split(image_file)[1]),
             ("fid", "2196998"),
             ("tbs", self.get_common_imgtbs())],
            [("file", os.path.split(image_file)[1], image_data)])
        
        req  = urllib2.Request(url, data=body, headers={"content-type": content_type})
        ret = self.opener.open(req).read()
        data = utils.parser_json(ret)
        try:
            content = {"src" : pic_url % (data["info"]["pic_id_encode"], img_ext),
                       "width" : data["info"]["fullpic_width"] if int(data["info"]["fullpic_width"]) <= 500 else 500,
                       "height" : data["info"]["fullpic_height"] if int(data["info"]["fullpic_height"]) <= 450 else 450,
                       "pic_type" : data["info"]["pic_type"]
                       }
            return content, data["info"]["full_sign1"]
        except KeyError:
            return False
        
    def new_tie(self, tieba_name, title, content, image_file=None, vedio=None, smiley=None):    
        params = {}
        vcode_ret = self.check_need_vcode(tieba_name)
        
        if vcode_ret is not None:
            code = raw_input("vcode save to %s > " % vcode_ret[0]).strip()
            params.update({"vcode" : code, "vcode_md5" : vcode_ret[1]})
            
        pic_dict = None
        params.update({"kw" : tieba_name, "ie" : "utf-8", "rich_text" : 1, "floor_num" : 0,
                  "tid" : 0, "fid" : self.get_forum_id(tieba_name), 
                  "mouse_pwd_isclick" : 1, "mouse_pwd_t" : utils.timestamp,
                  "anonymous" : 0, "tbs" : self.get_common_tbs(), 
                  "title" : title})
        
        if image_file is not None:
            pic_ret = self.upload_pic(image_file)
            if pic_ret:
                pic_dict = pic_ret[0]
                params.update({"hasuploadpic": 1, "picsign" : pic_ret[1]})
                
        params.update({"content" : utils.format_content(content, pic_dict, vedio, smiley)})        
        print params
        ret = self.api_request("/f/commit/thread/add", "POST", extra_data=params)
        print ret
            
    def get_verify_code(self):
        url = 'https://passport.baidu.com/v2/api/?logincheck&'         
        data = {
            "callback" : "bdPass.api.login._needCodestringCheckCallback",
            "tpl" : "mn",
            "charset" : "UTF-8",
            "index" : 0,
            "username" : self.username,
            "time" : utils.timestamp()
            }
        data_query = urllib.urlencode(data)
        url = "%s&%s" % (url, data_query)
        req = urllib2.Request(url)
        data = self.opener.open(req).read().strip()
        data = data[data.find("(") + 1: data.rfind(")")]
        data = eval(data, type('Dummy', (dict,), dict(__getitem__=lambda s,n:n))())
        codestring = data["codestring"]
        if codestring != "":
            url = "https://passport.baidu.com/cgi-bin/genimage?%s" % codestring
            req = urllib2.Request(url)
            ret_data = self.opener.open(req).read()
            pic_image = utils.get_cache_file("pic")
            with open(pic_image, "wb") as fp:
                fp.write(ret_data)
            self.loginfo("Verify code pic download ok!")
            return raw_input("piz input code > ").strip()    
        
    def reply_verify_code(self, type, **params):
        pass
    
    def reply_posts(self):
        pass
    
    def api_request(self, api, method="GET", extra_data=dict(), retry_limit=2, encoding=None, **params):    
        url = urlparse.urljoin("http://tieba.baidu.com/", api)
        data = self.apidata.copy()
        data.update(extra_data)
        data.update(params)
        for key in data:
            if callable(data[key]):
                data[key] = data[key]()
            if isinstance(data[key], (list, tuple, set)):
                data[key] = ",".join(map(str, list(data[key])))
            if isinstance(data[key], unicode):    
                data[key] = data[key].encode("utf-8")
                
        if method == "GET":        
            if data:
                query = urllib.urlencode(data)
                url = "%s?%s" % (url, query)
            req = urllib2.Request(url)
        elif method == "POST":
            body = urllib.urlencode(data)
            req = urllib2.Request(url, data=body)
            
        self.logdebug("API request url: %s", url)    
        start = time.time()    
        try:
            ret = self.opener.open(req)
        except Exception, e:    
            if retry_limit == 0:
                self.logdebug("API request error: url=%s error=%s",  url, e)
                return dict(result="network_error")
            else:
                retry_limit -= 1
                return self.api_request(api, method, extra_data, retry_limit, **params)
            
        if encoding is None:    
            raw = ret.read()
        else:    
            try:
                raw = ret.read().decode(encoding)
            except:    
                raw = ret.read()
        data = utils.parser_json(raw)       
        self.logdebug("API response %s: %s TT=%.3fs", api, data, time.time() - start )
        return data
    
    def test(self):
        # ret_data = self.api_request("/i/sys/user_json?v=%s" % utils.timestamp())
        # http://tieba.baidu.com/manager-apply/data/frs?dtype=json&ie=gbk&kw=bpython&fid=2196998&is_mgr=0&mgr_num=0&t=17b3ndkt9
        # ret_data = self.api_request("/i/commit", "POST", extra_data={"cmd" : "follow_all", "tbs": self.get_common_tbs()})
        pass
        

if __name__ == "__main__":    
    tieba_lib = TiebaLib(sys.argv[1], sys.argv[2])
    if tieba_lib.check_login():
        tieba_lib.new_tie("bpython", "【bpython】我就不说什么了", "测试表情哈!", smiley=("tsj", "t_0013"))
        
        # print tieba_lib.upload_pic("/home/evilbeast/Pictures/psb.jpg")
        # tiebas =  tieba_lib.get_favorite_tiebas()
        # for t in tiebas:
        #     print t, "--->", tieba_lib.get_forum_id(t)

        
        
        