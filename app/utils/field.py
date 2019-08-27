from wtforms import Field, StringField, SelectField
from wtforms.validators import DataRequired
from wtforms.utils import unset_value


class LabelsField(Field):

    def __init__(self, label=None, validators=None, key_name='label_name', value_name='label_value', **kwargs):
        super(LabelsField, self).__init__(label, validators, **kwargs)
        self.key_name = key_name
        self.value_name = value_name

    def process(self, formdata, data=unset_value):
        self.process_errors = []
        if data is unset_value:
            try:
                data = self.default()
            except TypeError:
                data = self.default

        self.object_data = data

        try:
            self.process_data(data)
        except ValueError as e:
            self.process_errors.append(e.args[0])

        if formdata is not None:
            if self.key_name in formdata and self.value_name in formdata:
                if len(formdata.getlist(self.key_name)) != len(formdata.getlist(self.value_name)):
                    self.process_errors.append('Label的key和value没有一一对应！')
                    self.data = {}
                    return
                if len(formdata.getlist(self.key_name)) == len(formdata.getlist(self.value_name)) == \
                        formdata.getlist(self.key_name).count('') == formdata.getlist(self.value_name).count(''):
                    self.data = {}
                    return
                if len(formdata.getlist(self.key_name)) != len(set(formdata.getlist(self.key_name))):
                    self.process_errors.append('Label的key有重复值！')
                    self.data = {}
                    return
                if '' in [x.strip() for x in formdata.getlist(self.key_name)]:
                    self.process_errors.append('Label的key不能有空值！')
                    self.data = {}
                    return
                self.raw_data = zip(formdata.getlist(self.key_name), formdata.getlist(self.value_name))
            else:
                self.raw_data = []

            try:
                self.process_formdata(self.raw_data)
            except ValueError as e:
                self.process_errors.append(e.args[0])

        try:
            for filter in self.filters:
                self.data = filter(self.data)
        except ValueError as e:
            self.process_errors.append(e.args[0])

    def process_formdata(self, valuelist):
        self.data = dict()
        if valuelist:
            for k, v in valuelist:
                self.data[k] = v

    def __iter__(self):
        if self.data:
            for k, v in self.data.items():
                label = StringField(_name=self.key_name, _form=None, _meta=self.meta)
                value = StringField(_name=self.value_name, _form=None, _meta=self.meta)
                label.process(None, k)
                value.process(None, v)
                yield label, value


class VolumesField(Field):

    def __init__(self, label=None, validators=None, **kwargs):
        super(VolumesField, self).__init__(label, validators, **kwargs)
        self.key_name = 'volume_name'
        self.value_name = 'bind_path'
        self.volumes = []

    def process(self, formdata, data=unset_value):
        self.process_errors = []
        if data is unset_value:
            try:
                data = self.default()
            except TypeError:
                data = self.default

        self.object_data = data

        try:
            self.process_data(data)
        except ValueError as e:
            self.process_errors.append(e.args[0])

        if formdata is not None:
            if self.key_name in formdata and self.value_name in formdata:
                if len(formdata.getlist(self.key_name)) != len(formdata.getlist(self.value_name)):
                    self.process_errors.append('volume_name和bind_path没有一一对应！')
                    self.data = {}
                    return
                if len(formdata.getlist(self.key_name)) == len(formdata.getlist(self.value_name)) == \
                        formdata.getlist(self.key_name).count('') == formdata.getlist(self.value_name).count(''):
                    self.data = {}
                    return
                if len(formdata.getlist(self.key_name)) != len(set(formdata.getlist(self.key_name))):
                    self.process_errors.append('volume_name有重复值！')
                    self.data = {}
                    return
                if '' in [x.strip() for x in formdata.getlist(self.key_name)]:
                    self.process_errors.append('volume_name不能有空值！')
                    self.data = {}
                    return
                if '' in [x.strip() for x in formdata.getlist(self.value_name)]:
                    self.process_errors.append('bind_path不能有空值！')
                    self.data = {}
                    return
                self.raw_data = zip(formdata.getlist(self.key_name), formdata.getlist(self.value_name))
            else:
                self.raw_data = []

            try:
                self.process_formdata(self.raw_data)
            except ValueError as e:
                self.process_errors.append(e.args[0])

        try:
            for filter in self.filters:
                self.data = filter(self.data)
        except ValueError as e:
            self.process_errors.append(e.args[0])

    def process_formdata(self, valuelist):
        self.data = dict()
        if valuelist:
            for k, v in valuelist:
                self.data[k] = {'bind': v, 'mode': 'rw'}

    def set_volumes(self, volumes):
        self.volumes = volumes

    def __iter__(self):
        if self.data:
            for k, v in self.data.items():
                volume = SelectField(_name=self.key_name, choices=self.volumes, _form=None, _meta=self.meta)
                container = StringField(_name=self.value_name, _form=None, _meta=self.meta)
                volume.process(None, k)
                container.process(None, v)
                yield volume, container
