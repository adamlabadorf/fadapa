"""
Python module to parse FastQC output data.
"""

from __future__ import print_function
from warnings import warn
from zipfile import ZipFile

class FastqcDataError(Exception): pass

class Fadapa(object):
    """
    Returns a parsed data object for given fastqc data file
    """

    def __init__(self, fp, **kwargs):
        """
        :arg fp: Name of fastqc_data text file, fastqc.zip file, or a file
                 pointer to a fastqc_data text file. If a file pointer is
                 provided, the user is expected to close the file after
                 Fadapa is finished.
        :type file_name: str or file pointer
        """
        if isinstance(fp,str) : # filename, .txt or .zip
            if fp.endswith('.zip') : # zip archive, open and extract .txt
                with ZipFile(fp) as f :
                    # check for fastqc_data.txt
                    data_fn = [_ for _ in f.namelist() if _.endswith('fastqc_data.txt')]
                    if len(data_fn) == 0 :
                        raise FastqcDataError('No file matching *fastqc_data.txt '
                               'found in zip archive, aborting')
                    elif len(data_fn) > 1 :
                        warn('Multiple files matching *fastqc_data.txt found '
                                'in zip archive:\n{}\nChoosing {}'.format(
                                    '\n'.join(data_fn),
                                    data_fn[0]
                                )
                            )
                    data_fn = data_fn[0]
                    with f.open(data_fn, **kwargs) as data_f :
                        self._content = data_f.read().decode().splitlines()
            elif fp.endswith('.txt') :
                with open(fp, **kwargs) as f :
                    self._content = f.read().splitlines()

        else : # file pointer
            self._content = fp.read().splitlines()

        self._m_mark = '>>'
        self._m_end = '>>END_MODULE'

    def summary(self):
        """
        Returns a list of all modules present in the content.
        Module begins  with  _m_mark ends with _m_end.

        :return: List of modules and their status.

        Sample module:

        >>Basic Statistics	pass
        #Measure	Value
        Filename	sample1.fastq
        >>END_MODULE

        """
        modules = [line.split('\t') for line in self._content
                   if self._m_mark in line and self._m_end not in line]
        data = [[i[2:], j] for i, j in modules]
        data.insert(0, ['Module Name', 'Status'])
        return data

    def content(self):
        """
        Print the contents of the given file.

        :return: None
        """
        for line in self._content:
            print(line)

    def raw_data(self, module):
        """
        Returns raw data lines for a given module name.

        :arg module: Name of module as returned by summary function.
        :type module: str.
        :return: List of strings which consists of raw data of module.
        """
        s_pos = next(self._content.index(x) for x in self._content
                     if module in x)
        e_pos = self._content[s_pos:].index(self._m_end)
        raw_data = self._content[s_pos:s_pos+e_pos+1]
        return raw_data

    def clean_data(self, module):
        """
        Returns a cleaned data for the given module.

        :arg module: name of module
        :type module: str
        :return List of strings containing the clean data of module.
        """
        data = [list(filter(None, x.split('\t')))
                for x in self.raw_data(module)[1:-1]]
        data[0][0] = data[0][0][1:]
        return data
