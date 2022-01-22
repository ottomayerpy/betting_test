import tornado.ioloop
import tornado.web
from tornado.options import define, options

from db import get_query, get_statistic, query_add, query_remove, query_update
from settings import DEBUG

define('port', default=8000, help='run on the given port', type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/api/add', ApiQueryHandler),
            (r'/api/get', ApiQueryHandler),
            (r'/api/remove', ApiQueryHandler),
            (r'/api/update', ApiQueryHandler),
            (r'/api/statistic', ApiStatisticHandler),
        ]
        settings = dict(
            debug=DEBUG,
        )
        super(Application, self).__init__(handlers, **settings)


class ApiQueryHandler(tornado.web.RequestHandler):
    """ Обработчик событий для запросов """
    async def post(self):
        """ Сохраняет запрос """
        answer = query_add(self.request.body)
        self.write(answer)

    async def get(self):
        """ Возвращает запрос """
        key = self.get_argument('key')
        query = get_query(key)
        self.write(query)

    async def delete(self):
        """ Удаляет запрос """
        key = self.get_argument('key')
        answer = query_remove(key)
        self.write(answer)

    async def put(self):
        """ Обновляет запрос """
        key = self.get_argument('key')
        answer = query_update(key, self.request.body)
        self.write(answer)


class ApiStatisticHandler(tornado.web.RequestHandler):
    """ Обработчик событий для статистики """
    async def get(self):
        """ Возвращает статистику """
        answer = get_statistic()
        self.write(answer)


if __name__ == "__main__":
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
