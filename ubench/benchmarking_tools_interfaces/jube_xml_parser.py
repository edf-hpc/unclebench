##############################################################################
#  This file is part of the UncleBench benchmarking tool.                    #
#        Copyright (C) 2019 EDF SA                                           #
#                                                                            #
#  UncleBench is free software: you can redistribute it and/or modify        #
#  it under the terms of the GNU General Public License as published by      #
#  the Free Software Foundation, either version 3 of the License, or         #
#  (at your option) any later version.                                       #
#                                                                            #
#  UncleBench is distributed in the hope that it will be useful,             #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              #
#  GNU General Public License for more details.                              #
#                                                                            #
#  You should have received a copy of the GNU General Public License         #
#  along with UncleBench. If not, see <http://www.gnu.org/licenses/>.        #
#                                                                            #
##############################################################################
# pylint: disable=no-member
""" JubeXMLParser class"""


import os
import sys
import re
import tempfile
import shutil
import logging
import lxml.etree as ET

def parse_xml(xml_path, parser=None):
    """
    Wrapper of ElementTree parse method to handle ParseError
    and IOError gracefully

    Args:
        xml_path: path of the xml file to parse
        parser: ElementTree xml parser
    """
    try:
        xml_element_tree = ET.parse(xml_path, parser)
    except ET.ParseError as p_error:
        msg = "Template file %s is malformed or not an xml"
        logging.error(msg,
                      xml_path, exc_info=False)
        logging.debug(msg+": "+str(p_error),
                      xml_path, exc_info=True)
        exit(1)
    except IOError as io_error:
        msg = "File %s cannot be loaded"
        logging.error(msg,
                      xml_path, exc_info=False)
        logging.debug(msg+": "+str(io_error),
                      xml_path, exc_info=True)
        exit(1)
    else:
        return xml_element_tree


class JubeXMLParser(object):  # pylint: disable=too-many-public-methods, too-many-instance-attributes
    """ JubeXMLParser """

    # There are three xml files that we need to load
    # - plattform
    # - bench
    # - config it is the xml generated by jube, we should load later after execution

    def __init__(self,
                 bench_xml_path_in,
                 bench_xml_files,
                 bench_xml_path_out='',
                 platforms_dir=''):
        """ Class constructor """

        self.bench_xml_path_in = bench_xml_path_in  # string
        self.bench_xml_path_out = bench_xml_path_out  # string
        self.bench_xml_files = bench_xml_files

        parser = ET.XMLParser(remove_blank_text=True, remove_comments=True)

        self.bench_xml = {
            xml_file: parse_xml(os.path.join(self.bench_xml_path_in, xml_file), parser)
            for xml_file in bench_xml_files
        }
        self.bench_xml_root = [
            bench_xml.getroot() for bench_xml in list(self.bench_xml.values())
        ]
        self.platforms_dir = platforms_dir
        self.platform_dir = tempfile.mkdtemp()
        self.platform_xml = []
        self.config_xml = ''


    def __del__(self):
        self.delete_platform_dir()

    def write_bench_xml(self):
        """ docstring """

        for name, xml_file in self.bench_xml.items():
            xml_file.write(os.path.join(self.bench_xml_path_out, name),
                           pretty_print=True)

        return True


    def write_platform_xml(self):
        """ docstring """

        for name, p_xml in self.platform_xml.items():
            p_xml.write(os.path.join(self.platform_dir, name))


    def delete_platform_dir(self):
        """ docstring """
        try:
            # it'll likely fail on python 3.5, but give it a try
            shutil.rmtree(self.platform_dir, ignore_errors=True)
        except Exception as err:
            pass


    def get_platform_dir(self):
        """ docstring """

        return self.platform_dir


    def remove_multisource(self):
        """ docstring """

        for b_xml in self.bench_xml_root:
            multisource = b_xml.find('multisource')
            if multisource is not None:
                b_xml.remove(multisource)


    def load_platforms_xml(self):
        """ docstring """

        self.generate_platform()
        return parse_xml(os.path.join(self.platform_dir, 'platforms.xml'))


    # The file is loaded later on, when the benchmark has already been run
    def load_config_xml(self, path):
        """ docstring """

        self.config_xml = parse_xml(path).getroot()


    def get_bench_outputdir(self):
        """ docstring """

        for b_xml in self.bench_xml_root:
            benchmark_tag = b_xml.findall('benchmark')
            if benchmark_tag:
                return benchmark_tag[0].get('outpath')


    def get_bench_resultfile(self):
        """ docstring """

        for b_xml in self.bench_xml_root:
            bench_root = b_xml.find('benchmark')
            if bench_root is not None:
                result = bench_root.find('result')
                if result is not None:
                    table = result.findall('table')
                    if table is not None:
                        return table[0].get('name') + '.dat'
        return None


    def get_bench_steps(self):
        """ docstring """

        steps = []
        for b_xml in self.bench_xml_root:
            # either is on inside tag jube or tag benchmark
            bench_root = b_xml.find('benchmark')

            if bench_root is not None:
                steps += [
                    step.get('name') for step in bench_root.findall('step')
                ]
            else:
                steps += [step.get('name') for step in b_xml.findall('step')]

        return steps


    def get_analyzer_names(self):
        """ docstring """

        analyzer_names = []
        for b_xml in self.bench_xml_root:
            bench_root = b_xml.find('benchmark')
            if bench_root is not None:
                analyzer_names += [step.get('name') for step in
                                   bench_root.findall('analyser')+bench_root.findall('analyzer')]
        # Look for analyzer name outside of benchmark tag
        if not analyzer_names:
            for bench_root in self.bench_xml_root:
                analyzer_names += [analyz.get('name') for analyz in
                                   bench_root.findall('analyser')+bench_root.findall('analyzer')]

        if not analyzer_names:
            analyzer_names.append('')

        return list(set(analyzer_names))


    def get_bench_parameterset(self):
        """ docstring """

        parameterset = []
        for b_xml in self.bench_xml_root:
            # either is on inside tag jube or tag benchmark
            bench_root = b_xml.find('benchmark')

            if bench_root is None:
                bench_root = b_xml

            parameterset += [
                parameterset.get('name')
                for parameterset in bench_root.findall('parameterset')
            ]

        return parameterset


    def get_bench_substituteset(self):
        """ docstring """

        substituteset = []
        for b_xml in self.bench_xml_root:

            # either is on inside tag jube or tag benchmark
            bench_root = b_xml.find('benchmark')
            if bench_root is None:
                bench_root = b_xml

            for element in bench_root.findall('substituteset'):

                # We add all substituteset except the one
                # that contains the init_with='platform.xml'
                if element.get('init_with') != 'platform.xml':
                    substituteset.append(element.get('name'))

        return substituteset


    def get_bench_fileset(self):
        """ docstring """
        fileset = []
        for b_xml in self.bench_xml_root:

            # either is on inside tag jube or tag benchmark
            bench_root = b_xml.find('benchmark')

            if bench_root is None:
                bench_root = b_xml

            fileset += [
                fileset.get('name')
                for fileset in bench_root.findall('fileset')
            ]

        return fileset


    def get_bench_multisource(self):  # pylint: disable=too-many-branches
        """ docstring """

        multisource_data = []
        for b_xml in self.bench_xml_root:

            multisource = b_xml.find('multisource')
            if multisource is not None:

                for source in multisource.findall('source'):
                    source_dict = {}
                    source_dict['protocol'] = source.get('protocol')
                    source_dict['name'] = source.get('name')

                    # File should be an array there could be many files for the benchmark
                    source_dict['files'] = []
                    for file_source in source.findall('file'):
                        source_dict['files'].append(file_source.text.strip())
                    source_dict['do_cmds'] = []

                    for do_cmd in source.findall('do'):
                        source_dict['do_cmds'].append(do_cmd.text.strip())

                    if source.find('revision') is not None:
                        source_dict['revision'] = []

                        for revision_source in source.findall('revision'):
                            source_dict['revision'].append(
                                revision_source.text.strip())

                    if source.find('branch') is not None:
                        source_dict['branch'] = []

                        for revision_source in source.findall('branch'):
                            source_dict['branch'] = revision_source.text.strip()

                    if source.find('url') is not None:
                        source_dict['url'] = source.find('url').text

                        if source_dict['protocol'] == 'git':
                            files = source_dict['files']

                            # Check if there is files to add else it adds the repo's name
                            if files:
                                source_dict['files'] = files
                                source_dict['files'].append(
                                    source_dict['url'].split('/')[-1].split('.')[0]
                                )
                            else:
                                source_dict['files'] = [
                                    source_dict['url'].split('/')[-1].split('.')[0]
                                ]

                    multisource_data.append(source_dict)

        return multisource_data


    def gen_bench_config(self):
        """ docstring """

        # bench_config is a dictionary of files and revision organized by protocol
        #
        # {'svn': {'simple_code': ['tests_dir'],
        #          'simple_code_revision': ['2018'],
        #          'input_revision': ['1000'],
        #          'input': ['file1', 'file2', 'file3']
        #          }
        # }

        bench_config = {}
        multisource_data = self.get_bench_multisource()

        for source in multisource_data:
            protocol_config = {}
            name = source['name']
            protocol = source['protocol']

            for file_source in source['files']:
                if name:
                    if name not in protocol_config:
                        protocol_config[name] = []
                    protocol_config[name].append(os.path.basename(file_source))

            if 'revision' in source:
                for revision_source in source['revision']:
                    if name:
                        name_revision = name + '_revision'
                        if name_revision not in protocol_config:
                            protocol_config[name_revision] = []
                        protocol_config[name_revision].append(revision_source)

            if protocol in bench_config:
                bench_config[protocol].update(protocol_config)
            else:
                bench_config[protocol] = protocol_config

        return bench_config


    def get_params_bench(self):
        """ Returns benchmark parameters

        Parses benchmark XML file and returns a list of tuples
        with `name` and `text` for all XML elements whose tag
        is `parameter`.
        """

        # Include variable of multisource
        self.add_bench_input(dict_options=None)
        parameters_list = []

        for b_xml in self.bench_xml_root:
            for parameter_node in b_xml.iter('parameter'):
                parameters_list.append(
                    (parameter_node.get('name'), parameter_node.text.strip()))

        return parameters_list


    def set_params_bench(self, dict_options):
        """ docstring """

        # Include variable of multisource
        self.add_bench_input(dict_options)
        parameters_list = []

        for b_xml in self.bench_xml_root:

            for parameter_node in b_xml.getiterator('parameter'):
                load_param = parameter_node.get('name')

                if load_param in list(dict_options.keys()):
                    parameters_list.append(
                        (load_param, parameter_node.text.strip(),
                         str(dict_options[load_param])))
                    parameter_node.text = str(dict_options[load_param])
                    upd = True  # pylint: disable=unused-variable

        return parameters_list

    def set_platform_path(self, platform_path):
        for b_xml in self.bench_xml_root:
            include_path = b_xml.find('include-path')

            if include_path is None:
                include_path = b_xml

            for path in include_path.findall('path'):
                path.text = platform_path



    def set_params_platform(self, dict_options):
        """ docstring """

        parameters_list = []
        for p_xml in list(self.platform_xml.values()):

            for parameter_node in p_xml.getroot().getiterator('parameter'):
                load_param = parameter_node.get('name')

                if load_param in list(dict_options.keys()):
                    parameters_list.append(
                        (load_param, parameter_node.text.strip(),
                         str(dict_options[load_param])))
                    parameter_node.text = str(dict_options[load_param])
                    upd = True  # pylint: disable=unused-variable

        return parameters_list


    def set_bench_execution(self):  # pylint: disable=too-many-branches
        """ docstring """

        # We perform the necessary modifications in the
        # XML file to enable only the execute step.

        # Get all steps
        for b_xml in self.bench_xml_root:  # pylint: disable=too-many-nested-blocks

            # Either is on inside tag jube or tag benchmark
            bench_root = b_xml.find('benchmark')

            if bench_root is None:
                bench_root = b_xml

            for step in bench_root.findall('step'):
                if step.get('name') != "execute" and step.get(
                        'depend') != 'execute':
                    step.set('tag', 'noexecute')
                else:
                    step.set('tag', '!noexecute')

                    if step.get('name') == 'execute':
                        step.attrib.pop('depend')

                        for use_tag in step.findall('use'):
                            if use_tag.text.strip(
                            ) in self.get_bench_substituteset(
                            ) + self.get_bench_fileset():
                                step.remove(use_tag)

            # We look for a fileset benchfiles and we add to the step execute
            # We generate a filseset for bench_files
            file_bench_element = None

            index_insert = -1
            for idx, element in enumerate(bench_root):

                if element.get('name') == 'bench_files':
                    # we insert a filset with the content of bench_files
                    file_bench_element = ET.Element(
                        'fileset', attrib={'name': 'bench_files_links'})

                    for parameter in element.findall('parameter'):
                        if os.path.isfile(parameter.text):
                            link = ET.SubElement(file_bench_element, 'link')
                            link.text = parameter.text
                            index_insert = idx

                    break

            if index_insert > 0:
                bench_root.insert(index_insert, file_bench_element)

            if 'bench_files' in self.get_bench_parameterset():
                step_execute = bench_root.findall("step[@name='execute']")

                if step_execute:  # not empty
                    present_params = []  # pylint: disable=unused-variable
                    use = ET.Element('use')
                    use.text = "bench_files_links"
                    step_execute[0].insert(0, use)

                    # remove bench config
                    for element in step_execute[0].findall('use'):
                        if element.text == "bench_config":
                            step_execute.remove(element)
                            break

            # We treat the case when we include other files
            # we remove external dependences as its always compile step
            include_tags = bench_root.findall('include')
            if include_tags:

                for element in include_tags:

                    if ((element.get('from')) not in self.bench_xml_files) and \
                       ((element.get('path') == "step")):
                        bench_root.remove(element)


    def add_bench_input(self, dict_options=None):
        """ Adds information concerning benchmark input files """
        # pylint: disable=too-many-locals, too-many-branches, too-many-statements

        # Adding multisource files as JUBE variables
        bench_config = self.gen_bench_config()
        if not bench_config:  # no information available
            return 0

        for b_xml in self.bench_xml_root:  # pylint: disable=too-many-nested-blocks
            benchmark = b_xml.find('benchmark')

            if benchmark is not None:

                # If the element arlready exist we do nothing
                if benchmark.findall("parameterset[@name='ubench_config']"):
                    return None

                config_element = ET.Element('parameterset',
                                            attrib={'name': 'ubench_config'})
                benchmark.insert(0, config_element)

                # I have to insert this element into the main existing benchmark
                files_element = ET.Element('fileset',
                                           attrib={'name': 'ubench_files'})

                benchmark.insert(1, files_element)
                benchmark_name = benchmark.get('name').lower()
                link = ET.SubElement(files_element,
                                     'link',
                                     attrib={
                                         'name': benchmark_name,
                                         'rel_path_ref': 'external'
                                     })
                link.text = "$UBENCH_RESOURCE_DIR/{0}/".format(benchmark_name)

                # pylint: disable=consider-iterating-dictionary
                for protocol in list(bench_config.keys()):

                    # add another level
                    for name, options in bench_config[protocol].items():
                        # if '-revision' in name:
                        # Handling several revision
                        # new_name = name.replace('-revision','')
                        num_items = list(bench_config[protocol].keys())

                        if (
                                protocol == 'svn' or protocol == 'git'
                        ) and not '_revision' in name and len(num_items) > 1:
                            name_id = name + '_id'
                            custom_param = ET.SubElement(
                                config_element,
                                'parameter',
                                attrib={'name': name_id})
                            custom_param.text = ','.join(
                                ['{0}'.format(x) for x in range(len(options))])

                            custom_param = ET.SubElement(config_element,
                                                         'parameter',
                                                         attrib={
                                                             'name': name,
                                                             'mode': 'python'
                                                         })
                            revision_name = name + '_revision'

                            new_paths = [
                                '${{{0}}}_{1}'.format(revision_name, item)
                                for item in options
                            ]
                            custom_param.text = str(
                                new_paths) + '[${{{0}}}]'.format(name_id)

                        else:

                            name_id = name + '_id'

                            custom_param = ET.SubElement(
                                config_element,
                                'parameter',
                                attrib={'name': name_id})
                            custom_param.text = ','.join(
                                ['{0}'.format(x) for x in range(len(options))])

                            custom_param = ET.SubElement(config_element,
                                                         'parameter', attrib={
                                                             'name': name,
                                                             'mode': 'python'})
                            custom_param.text = str(
                                options) + '[${{{0}}}]'.format(name_id)

                    # create link for benchmark directory
                    for name, options in bench_config[protocol].items():
                        if not '_revision' in name:
                            link = ET.SubElement(
                                files_element,
                                'link',
                                attrib={'rel_path_ref': 'external'})
                            if protocol == 'svn' or protocol == 'git':
                                link.text = '$UBENCH_RESOURCE_DIR/{0}/{1}/${{{2}}}'.format(
                                    benchmark_name.lower(), protocol, name)
                            else:
                                link.text = '$UBENCH_RESOURCE_DIR/{0}/${{{1}}}'.format(
                                    benchmark_name.lower(), name)

            ### Adding special tags to all steps
            if benchmark is None:
                steps = b_xml.findall("step")
            else:
                steps = benchmark.findall("step")

            for step in steps:  # not empty
                present_params = []
                for use in step.findall('use'):
                    present_params.append(use.text.strip())

                for name in ['ubench_config', 'ubench_files']:
                    use = ET.Element('use')
                    use.text = name
                    if name not in present_params and 'bench_files_links' not in present_params:
                        step.insert(0, use)

    def add_custom_nodes_stub(self, custom_nodes_numbers, custom_nodes_ids):
        """ docstring """
        # pylint: disable=too-many-locals, too-many-branches

        found = False  # pylint: disable=unused-variable
        local_tree = None  # pylint: disable=unused-variable
        file_path = ''  # pylint: disable=unused-variable

        # Add or modify custom nodes configuration section
        for b_xml in self.bench_xml_root:  # pylint: disable=too-many-nested-blocks

            parents = self.get_parents_from_child_tag(b_xml, 'step', 'execute')

            for p in parents:  # pylint: disable=invalid-name

                custom_element = ET.Element('parameterset',
                                            attrib={'name': 'custom_parameter'})

                custom_id = ET.SubElement(custom_element, 'parameter',
                                          attrib={'name':'custom_id'})

                custom_id.text = (',').join(
                    map(str, list(range(0, len(custom_nodes_numbers)))))

                custom_nodes = ET.SubElement(custom_element, 'parameter',
                                             attrib={'name':'custom_nodes',
                                                     'mode':'python',
                                                     'type':'int'})
                custom_nodes.text = str(list(map(
                    int, custom_nodes_numbers))) + '[$custom_id]'

                if custom_nodes_ids:
                    custom_nodes_id = ET.SubElement(custom_element, 'parameter',
                                                    attrib={'name':'custom_nodes_id',
                                                            'mode':'python',
                                                            'type':'string',
                                                            'separator':'??'})
                    custom_nodes_id.text = str(
                        custom_nodes_ids) + '[$custom_id]'

                    custom_sub = {}
                    custom_sub_keys = ['submit', 'submit_singleton']
                    for ck in custom_sub_keys:  # pylint: disable=invalid-name
                        # pylint: disable=duplicate-key
                        custom_sub[ck] = ET.SubElement(custom_element, 'parameter',
                                                       attrib={'name':'custom_' + ck,
                                                               'separator':'??',
                                                               'mode':'python',
                                                               'type':'string',
                                                               'separator':'??'})
                        custom_sub[ck].text = '['
                        for el in custom_nodes_ids:  # pylint: disable=invalid-name
                            if el != None:
                                custom_sub[
                                    ck].text += "'$" + ck + " -w $custom_nodes_id ',"
                            else:
                                custom_sub[ck].text += "'$" + ck + " ',"
                        custom_sub[ck].text = custom_sub[
                            ck].text[:-1] + '][$custom_id]'

                p.insert(0, custom_element)

            # Add <use> custom_paremeters </use> in the appropriate section
            # for node in local_tree.iter('step'):

            for node in b_xml.getiterator('step'):
                local_found = False
                need_system_parameters = False

                for subnode in node.getiterator('use'):
                    if subnode.text == 'custom_parameter':
                        local_found = True
                    if 'system_parameters' in subnode.text:
                        need_system_parameters = True

                if not local_found and need_system_parameters:
                    update = True  # pylint: disable=unused-variable
                    use_custom = ET.Element('use')
                    use_custom.text = 'custom_parameter'
                    node.insert(0, use_custom)

            # Add a node names column in result table
            # for node in local_tree.iter('table'):
            for node in b_xml.getiterator('table'):
                local_found = False

                for column in node.findall('column'):
                    if column.text == 'custom_nodes_id':
                        local_found = True
                        if not custom_nodes_ids:
                            update = True
                            node.remove(column)

                if not local_found and custom_nodes_ids:
                    update = True
                    custom_column = ET.Element('column')
                    custom_column.text = 'custom_nodes_id'
                    node.append(custom_column)


    def get_parents_from_child_tag(self, node, child_tag, child_name=None):
        """ docstring """

        result = []

        if not list(node):
            return []

        for child in list(node):
            if child.tag == child_tag and (child.get('name') == child_name
                                           or not child_name):
                result.append(node)
            result = result + self.get_parents_from_child_tag(
                child, child_tag, child_name)

        return result


    def substitute_element_text(self, element, element_name, pattern, new_text):
        """ Substitute pattern with new_text in the text from an xml node called
        element with attribute name element_name. The xml file is found in
        benchmark result root path.

        Args:
            element (str): name of the xml node to be modified.
            element_name (str): value of the 'name' attribute of the node to be modified.
            pattern (str): pattern to be modified
            new_text (str):
        """

        for b_xml in self.bench_xml_root:
            for el in b_xml.getiterator(element):  # pylint: disable=invalid-name
                if not element_name or el.get('name') == element_name:
                    if re.findall(pattern, el.text):
                        el.text = re.sub(pattern, new_text, el.text)


    def get_dirs(self, dir_path):  # pylint: disable=no-self-use
        """ docstring """

        return [
            d for d in os.listdir(dir_path)
            if os.path.isdir(os.path.join(dir_path, d))
        ]


    def generate_platform(self):
        """ docstring """

        # Generate a file with all platform paths
        platform_dir = self.platforms_dir
        template_xml = parse_xml(os.path.join(platform_dir, 'template.xml'))

        platform_directories = self.get_dirs(platform_dir)
        include_dir = template_xml.getroot().find('include-path')
        platform_element = ET.Element('path')
        platform_element.text = os.path.join(platform_dir)
        include_dir.insert(0, platform_element)

        for platform in platform_directories:
            subdirs = self.get_dirs(os.path.join(platform_dir, platform))
            if subdirs:
                platform_element = ET.Element(
                    'path', attrib={'tag': ','.join(subdirs)})  # An element for the main directory

                platform_element.text = os.path.join(platform_dir, platform)
                include_dir.insert(0, platform_element)

                for subdir in subdirs:
                    platform_element = ET.Element(
                        'path', attrib={'tag': subdir.lower()})
                    platform_element.text = os.path.join(
                        platform_dir, platform + '/' + subdir)
                    include_dir.insert(0, platform_element)
            else:
                platform_element = ET.Element('path',
                                              attrib={'tag': platform.lower()})
                platform_element.text = os.path.join(platform_dir, platform)
                include_dir.insert(0, platform_element)

        template_xml.write(os.path.join(self.platform_dir, 'platforms.xml'))


    def load_platform_xml(self, platform_name):
        """ docstring """

        platforms_xml = self.load_platforms_xml()
        path_raw = ''
        paths_platform_xml = {}
        for path in platforms_xml.getroot().iter('path'):
            if path.get('tag') == platform_name:
                path_raw = path.text
                platform_path = os.path.join(path_raw, 'platform.xml')
                nodetype_path = os.path.join(path_raw, 'nodetype.xml')

                if os.path.exists(platform_path):
                    paths_platform_xml['platform.xml'] = parse_xml(platform_path)
                    path.text = self.platform_dir

                elif os.path.exists(nodetype_path):
                    platform_updir = os.path.dirname(path_raw)
                    path.text = self.platform_dir
                    paths_platform_xml['nodetype.xml'] = parse_xml(nodetype_path)
                    paths_platform_xml['platform.xml'] = parse_xml(
                        os.path.join(platform_updir, 'platform.xml'))

        self.platform_xml = paths_platform_xml
        platforms_xml.write(os.path.join(self.platform_dir, 'platforms.xml'))


    def get_params_platform(self, platform_name):
        """ Returns platform parameters

        Parses platform XML file and returns a list of tuples
        with `name` and `text` for all XML elements whose tag
        is `parameter`.
        """

        parameters_list = []
        self.load_platform_xml(platform_name)
        for platform_xml in list(self.platform_xml.values()):
            for parameter_node in platform_xml.getiterator('parameter'):
                if parameter_node.text:
                    parameters_list.append((parameter_node.get('name'),
                                            parameter_node.text.strip()))

        return parameters_list


class JubeXMLConfig(object):

    def __init__(self,path):

        self.config_xml = parse_xml(path).getroot()


    def get_job_logfiles(self):

        config_xml_file = self.config_xml
        log_files = []
        for node in config_xml_file.getiterator('parameter'):
            if (node.get('name') == 'outlogfile') or (
                    node.get('name') == 'errlogfile'):
                if node.text:
                    log_files.append(node.text.strip())
        return log_files

    def get_analyse_files(self):
        """ docstring """

        config_xml_file = self.config_xml
        analyse_files = []
        for node in config_xml_file.getiterator('analyse'):
            for subnode in node.getiterator('file'):
                if subnode.text:
                    analyse_files.append(subnode.text.strip())
        return analyse_files


    def get_result_cvsfile(self):
        """ docstring """

        config_xml_file = self.config_xml
        cvs_file_name = None
        for node in config_xml_file.getiterator('table'):
            if node.get('style') == "csv":
                cvs_file_name = node.get("name")
                return cvs_file_name


    def get_result_transpose(self):
        """ docstring """

        config_xml_file = self.config_xml
        for node in config_xml_file.getiterator('table'):
            if node.get('transpose') is not None:
                transpose = node.get('transpose').strip().lower() == "true"
            else:
                transpose = False
        return transpose
