# -*- coding: utf-8 -*-

import os
import sys
import tarfile

from pyload.plugins.base.extractor import ArchiveError, BaseExtractor, CRCError


class UnTar(BaseExtractor):
    __name__ = "UnTar"
    __type__ = "extractor"
    __version__ = "0.05"
    __status__ = "stable"

    __description__ = """TAR extractor plugin"""
    __license__ = "GPLv3"
    __authors__ = [("Walter Purcaro", "vuolter@gmail.com")]

    VERSION = "{}.{}.{}".format(
        sys.version_info[0], sys.version_info[1], sys.version_info[2]
    )

    @classmethod
    def isarchive(cls, filename):
        try:
            return tarfile.is_tarfile(os.fsdecode(filename))
        except Exception:
            return False

    @classmethod
    def find(cls):
        return sys.version_info[:2] >= (2, 5)

    def list(self, password=None):
        with tarfile.open(self.filename) as t:
            self.files = [os.path.join(self.dest, _f) for _f in t.getnames()]
        return self.files

    def verify(self, password=None):
        try:
            t = tarfile.open(self.filename, errorlevel=1)

        except tarfile.CompressionError as exc:
            raise CRCError(exc)

        except (OSError, tarfile.TarError) as exc:
            raise ArchiveError(exc)

        else:
            t.close()

    def extract(self, password=None):
        self.verify(password)

        try:
            with tarfile.open(self.filename, errorlevel=2) as t:
                def is_within_directory(directory, target):
                    
                    abs_directory = os.path.abspath(directory)
                    abs_target = os.path.abspath(target)
                
                    prefix = os.path.commonprefix([abs_directory, abs_target])
                    
                    return prefix == abs_directory
                
                def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                
                    for member in tar.getmembers():
                        member_path = os.path.join(path, member.name)
                        if not is_within_directory(path, member_path):
                            raise Exception("Attempted Path Traversal in Tar File")
                
                    tar.extractall(path, members, numeric_owner=numeric_owner) 
                    
                
                safe_extract(t, self.dest)
                self.files = t.getnames()
            return self.files

        except tarfile.ExtractError as exc:
            self.log_warning(exc)

        except tarfile.CompressionError as exc:
            raise CRCError(exc)

        except (OSError, tarfile.TarError) as exc:
            raise ArchiveError(exc)
