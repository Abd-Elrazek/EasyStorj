from PyQt4 import QtCore, QtGui
from qt_interfaces.register_ui_new import Ui_UI_Register
from login import LoginUI
from utilities.tools import Tools
import json
import storj
from utilities.log_manager import logger


# Register section
class RegisterUI(QtGui.QMainWindow):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        # register UI
        self.register_ui = Ui_UI_Register()
        self.register_ui.setupUi(self)

        self.register_ui.password.setEchoMode(QtGui.QLineEdit.Password)
        self.register_ui.password_2.setEchoMode(QtGui.QLineEdit.Password)

        QtCore.QObject.connect(self.register_ui.register_bt,
                               QtCore.SIGNAL('clicked()'),
                               self.register)  # validate and register user

    def register(self):
        # validate fields
        self.email = self.register_ui.email.text()
        self.password = self.register_ui.password.text()
        self.password_repeat = self.register_ui.password_2.text()
        self.bridge_api_url = str(self.register_ui.bridge_url.text()).strip()  # get bridge api url

        if len(self.bridge_api_url) < 6:  # xxx.yy
            self.bridge_api_url = 'https://api.storj.io/'

        self.tools = Tools()
        success = False
        if self.email != '' and self.password != '' and self.password_repeat != '':
            if self.password == self.password_repeat:
                if (self.tools.check_email(self.email)):
                    # take login action
                    try:
                        self.storj_client = storj.Client(None, '', storj_bridge=self.bridge_api_url).user_create(str(self.email).strip(), str(self.password).strip())
                        success = True
                    except storj.exception.StorjBridgeApiError as e:
                        j = json.loads(str(e))
                        if j[0]['error'] == 'Email is already registered':
                            QtGui.QMessageBox.about(self, 'Warning',
                                                    'User with this e-mail is \
                                                    already registered! Please \
                                                    login or try a different \
                                                    e-mail!')
                        else:
                            QtGui.QMessageBox.about(self, 'Unhandled exception',
                                                    'Exception: ' + str(e))
                else:
                    QtGui.QMessageBox.about(self, 'Warning', 'Your e-mail \
                                            seems to be invalid! Please check \
                                            e-mail and try again')
            else:
                QtGui.QMessageBox.about(self, 'Warning',
                                        'Given passwords are different! Please\
                                        check and try again!')
        else:
            QtGui.QMessageBox.about(self, 'Warning',
                                    'Please fill out all fields!')

        if success:
            msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Information, 'Success',
                                       'Successfully registered to Storj!'
                                       'Verify your email by clicking on the'
                                       'link that was sent to you.'
                                       'Then, you can login.',
                                       QtGui.QMessageBox.Ok)

            logger.debug('New user registrated')
            logger.debug('Email: %s' % self.email)
            logger.debug('Password: %s' % self.password)
            result = msgBox.exec_()
            if result == QtGui.QMessageBox.Ok:
                self.login_window = LoginUI(self)
                self.login_window.show()
                self.close()
                # initial_window.hide()
