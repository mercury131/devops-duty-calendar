import hashlib
import json
import os
import time
from typing import Dict, cast

import ldap

from cachelib.simple import SimpleCache

from flask import  current_app, session

cache = SimpleCache()


class Authentication:

    USERS_FILENAME = "users.json"

    def __init__(self, data_folder: str, password_salt: str, failed_login_delay_base: int) -> None:
        self.contents = {}  # type: Dict
        with open(os.path.join(".", data_folder, self.USERS_FILENAME)) as file:
            self.contents = json.load(file)
        self.password_salt = password_salt
        self.failed_login_delay_base = failed_login_delay_base
        self.data_folder = data_folder

    def ldap_auth(self, username, password, check):
        #
        check = check
        if check == "checkadmin":
            checkadmin = "checkadmin"
        else:
            checkadmin = ''
        try:
            CACert = current_app.config["CACERT"]
            ldapserver = current_app.config["LDAPSERVER"]
            username = username
            password = password
            ou = current_app.config["OU"]
            domain = current_app.config["DOMAIN"]
            allowgroup_ro = current_app.config["ALLOWGROUP_RO"]
            allowgroup_rw = current_app.config["ALLOWGROUP_RW"]
            ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, CACert)
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_HARD)
            # Disable ssl check
            #ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
            connect = ldap.initialize("ldaps://" + ldapserver)
            connect.set_option(ldap.OPT_REFERRALS, 0)
            connect.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
            connect.set_option(ldap.OPT_X_TLS,ldap.OPT_X_TLS_DEMAND)
            connect.set_option( ldap.OPT_X_TLS_DEMAND, True )
            connect.set_option( ldap.OPT_DEBUG_LEVEL, 255 )
            connect.simple_bind_s(username, password)
            result = connect.search_s(ou,ldap.SCOPE_SUBTREE,('userPrincipalName=' + username + '@' + domain),['memberOf'])
            groups  = result[0][1]['memberOf']
            for group in groups:
                if str(group)[2:][:-1] == allowgroup_ro:
                    return True
                elif str(group)[2:][:-1] == allowgroup_rw:
                    if checkadmin == "checkadmin":
                        return "admin"
                    else:
                        return True
        except Exception:
            return False


    def is_valid(self, username: str, password: str) -> bool:
        
        use_ldap=current_app.config["USE_LDAP"]
        if use_ldap == 'true':
            #return True
            auth_in_ldap=self.ldap_auth(str(username), str(password), '')
            if auth_in_ldap is True:
                is_admin=self.ldap_auth(str(username), str(password), str('checkadmin'))
                if is_admin == 'admin' :
                    session['admin'] = 'true'
                else:
                    session['admin'] = 'no'
                return True
            else:
                return False
        else:
            if username not in self.contents:
                self._failed_attempt(username)
                return False
            if self._hash_password(password) != self.contents[username]["password"]:
                self._failed_attempt(username)
                return False
            return True

    def user_data(self, username: str) -> Dict:
        use_ldap=current_app.config["USE_LDAP"]
        if use_ldap == 'true':
            return username
        else:
            return cast(Dict, self.contents[username])

    def add_user(self, username: str, plaintext_password: str, default_calendar: str) -> None:
        if username in self.contents:
            raise ValueError("Username {} already exists".format(username))
        hashed_password = self._hash_password(plaintext_password)
        self.contents[username] = {
            "username": username,
            "password": hashed_password,
            "default_calendar": default_calendar,
            "ics_key": "an_ics_key",
        }
        self._save()

    def delete_user(self, username: str) -> None:
        self.contents.pop(username)
        self._save()

    def _hash_password(self, plaintext_password: str) -> str:
        hash_algoritm = hashlib.new("sha256")
        hash_algoritm.update((plaintext_password + self.password_salt).encode("UTF-8"))
        return hash_algoritm.hexdigest()

    def _save(self) -> None:
        with open(os.path.join(".", self.data_folder, self.USERS_FILENAME), "w") as file:
            json.dump(self.contents, file)

    def _failed_attempt(self, username: str) -> None:
        key = "LF_{}".format(username)
        attempts = cache.get(key)
        if attempts is None:
            attempts = 0
        else:
            attempts = int(attempts) + 1
        wait = self.failed_login_delay_base ** attempts
        cache.set(key, attempts, timeout=7200)  # Keep for 2h
        time.sleep(wait)
