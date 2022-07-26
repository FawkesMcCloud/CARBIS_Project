import sqlite3
import logging


class Config:
    def __init__(self, database_name="config.db"):
        self.config = None

        self.database_name = database_name
        try:
            self.con = sqlite3.connect(self.database_name)
        except sqlite3.Error as e:
            logging.error(e)

        self.create_default()
        self.load_config("default")

    def load_config(self, profile):
        """
        Loads config with specified profile name
        :param profile: profile name
        :return: bool
        """
        if self.config is not None and self.config["profile"] == profile:
            return True

        cur = self.con.cursor()
        cur.execute('select * from CONFIG where name=?', (profile,))
        row = cur.fetchone()

        if row is None:
            return False

        config = {"profile": row[0],
                    "lang": row[1],
                    "url": row[2],
                    "token": row[3]}
        self.config = config
        logging.info("successfully loaded config")
        return True

    def change_token(self, token):
        """
        Changes token in current config profile
        :param token:
        :return:
        """
        cur = self.con.cursor()
        profile = self.config["profile"]
        cur.execute('UPDATE CONFIG SET api = ? WHERE name = ?', (token, profile))
        self.config["token"] = token

        self.con.commit()
        logging.debug("changed token")

    def change_base_url(self, url):
        """
        Changes base url in current config profile
        :param url:
        :return:
        """
        cur = self.con.cursor()
        profile = self.config["profile"]
        cur.execute('UPDATE CONFIG SET url = ? WHERE name = ?', (url, profile))
        self.config["url"] = url

        self.con.commit()
        logging.debug("changed url")

    def change_language(self):
        """
        Changes language between EN/RU
        :return:
        """
        if self.config["lang"] == "ru":
            self.config["lang"] = "en"
        else:
            self.config["lang"] = "ru"

        cur = self.con.cursor()
        profile = self.config["profile"]
        lang = self.config["lang"]
        cur.execute('UPDATE CONFIG SET lang = ? WHERE name = ?', (lang, profile))
        self.con.commit()
        logging.debug("changed language")

    def create_default(self):
        """
        Creates default config table without API token.
        :return:
        """
        cur = self.con.cursor()
        default_URL = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/address"
        cur.execute('CREATE TABLE IF NOT EXISTS CONFIG (name text not null UNIQUE, lang text,\n'
                    '                        url text,\n'
                    '                        api text )')
        cur.execute("INSERT OR IGNORE INTO CONFIG VALUES (?,?,?,?)", ('default', 'ru', default_URL, ''))

        self.con.commit()
        logging.info("created default table")

    def show_config(self):
        return f"URL: {self.config['url']}\n" \
               f"Language: {self.config['lang']}\n" \
               f"Token: {self.config['token'][:5]}"

    def __getitem__(self, item):
        return self.config[item]
