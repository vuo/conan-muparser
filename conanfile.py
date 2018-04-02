from conans import AutoToolsBuildEnvironment, ConanFile, tools
import os
import platform

class MuParserConan(ConanFile):
    name = 'muparser'

    source_version = '2.2.5'
    package_version = '2'
    version = '%s-%s' % (source_version, package_version)

    requires = 'llvm/3.3-2@vuo/stable', \
               'vuoutils/1.0@vuo/stable'
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'http://muparser.beltoforion.de/'
    license = 'http://beltoforion.de/article.php?a=muparser&hl=en&p=licence'
    description = 'A library for parsing mathematical expressions'
    source_dir = 'muparser-%s' % source_version
    build_dir = '_build'
    libs = {
        'muparser': 2,
    }

    def requirements(self):
        if platform.system() == 'Linux':
            self.requires('patchelf/0.10pre-1@vuo/stable')
        elif platform.system() != 'Darwin':
            raise Exception('Unknown platform "%s"' % platform.system())

    def source(self):
        tools.get('https://github.com/beltoforion/muparser/archive/v%s.tar.gz' % self.source_version,
                  sha256='0666ef55da72c3e356ca85b6a0084d56b05dd740c3c21d26d372085aa2c6e708')

        self.run('mv %s/License.txt %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

    def build(self):
        import VuoUtils
        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            autotools = AutoToolsBuildEnvironment(self)

            # The LLVM/Clang libs get automatically added by the `requires` line,
            # but this package doesn't need to link with them.
            autotools.libs = []

            autotools.flags.append('-Oz')

            if platform.system() == 'Darwin':
                autotools.flags.append('-mmacosx-version-min=10.10')
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
            with tools.chdir('lib'):
                VuoUtils.fixLibs(self.libs, self.deps_cpp_info)

    def package(self):
        if platform.system() == 'Darwin':
            libext = 'dylib'
        elif platform.system() == 'Linux':
            libext = 'so'

        self.copy('*.h', src='%s/include' % self.source_dir, dst='include/muParser')
        self.copy('libmuparser.%s' % libext, src='%s/lib' % self.build_dir, dst='lib')

        self.copy('%s.txt' % self.name, src=self.source_dir, dst='license')

    def package_info(self):
        self.cpp_info.libs = ['muparser']
