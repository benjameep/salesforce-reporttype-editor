import streamlit as st
from lib.parser import parse_xml, unparse_xml

data = {
    'baseObject': '',
    'category': 'other',
    'label': '',
    'description': '',
    'fields': [],
}

uploaded_file = st.file_uploader("Edit an existing reportType-meta.xml file", type="reportType-meta.xml")

if uploaded_file is not None:
    data = parse_xml(uploaded_file.getvalue())

data['baseObject'] = st.text_input('baseObject', data['baseObject'])
CATEGORIES = [ 'accounts', 'opportunities', 'forecasts', 'cases', 'leads', 'campaigns', 'activities', 'busop', 'products', 'admin', 'territory', 'territory2', 'usage_entitlement' 'wdc', 'calibration', 'other', 'content', 'quotes', 'individual', 'employee', 'data_cloud', 'commerce', 'flow', 'semantic_model' ]
data['category'] = st.selectbox('category', CATEGORIES, index=CATEGORIES.index(data['category']))
data['label'] = st.text_input('label', data['label'])
data['description'] = st.text_area('description', data['description'])

st.write('Fields')
data['fields'] = st.data_editor(data['fields'], use_container_width=True, num_rows='dynamic')

for field in data['fields']:
    if field['default'] is None:
        field['default'] = False
    if not field['section'] or not field['field']:
        st.error('All fields must have a section and a field')
        break

st.code(unparse_xml(data).decode(), language='xml')