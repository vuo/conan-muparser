from conans import AutoToolsBuildEnvironment, ConanFile, tools
import os
import platform

class MuParserConan(ConanFile):
    name = 'muparser'

    source_version = '2.2.5'
    package_version = '2'
    version = '%s-%s' % (source_version, package_version)

    requires = 'llvm/3.3-2@vuo/stable'
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'http://muparser.beltoforion.de/'
    license = 'http://beltoforion.de/article.php?a=muparser&hl=en&p=licence'
    description = 'A library for parsing mathematical expressions'
    source_dir = 'muparser-%s' % source_version
    build_dir = '_build'

    def source(self):
        tools.get('https://github.com/beltoforion/muparser/archive/v%s.tar.gz' % self.source_version,
                  sha256='0666ef55da72c3e356ca85b6a0084d56b05dd740c3c21d26d372085aa2c6e708')

    def build(self):
        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            autotools = AutoToolsBuildEnvironment(self)

            # The LLVM/Clang libs get automatically added by the `requires` line,
            # but this package doesn't need to link with them.
            autotools.libs = []

            autotools.cxx_flags.append('-Oz')
            # autotools.cxx_flags.append('-Wno-error')

            if platform.system() == 'Darwin':
                autotools.cxx_flags.append('-mmacosx-version-min=10.10')
                autotools.link_flags.append('-Wl,-headerpad_max_install_names')
                autotools.link_flags.append('-Wl,-install_name,@rpath/libmuparser.dylib')

            env_vars = {
                'CC' : self.deps_cpp_info['llvm'].rootpath + '/bin/clang',
                'CXX': self.deps_cpp_info['llvm'].rootpath + '/bin/clang++',
            }
            with tools.environment_append(env_vars):
                autotools.configure(configure_dir='../%s' % self.source_dir,
                                    build=False,
                                    host=False,
                                    args=['--quiet',
                                          '--enable-shared',
                                          '--disable-samples',
                                          '--prefix=%s' % os.getcwd()])
                autotools.make(args=['--quiet'])

    def package(self):
        self.copy('*.h', src='%s/include' % self.source_dir, dst='include/muParser')
        self.copy('libmuparser.dylib', src='%s/lib' % self.build_dir, dst='lib')

    def package_info(self):
        self.cpp_info.libs = ['muparser']
