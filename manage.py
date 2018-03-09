from flask_script import Shell, Manager
from app import app


def _make_context():
    return dict(app=app)

manager = Manager(app)
manager.add_command("shell", Shell(make_context=_make_context))

if __name__ == "__main__":
    manager.run()
