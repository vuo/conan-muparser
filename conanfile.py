from conans import ConanFile, CMake, tools
import os
import platform

class MuParserConan(ConanFile):
    name = 'muparser'

    source_version = '2.3.2'
    package_version = '0'
    version = '%s-%s' % (source_version, package_version)

    build_requires = (
        'llvm/5.0.2-1@vuo/stable',
        'macos-sdk/11.0-0@vuo/stable',
    )
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'http://muparser.beltoforion.de/'
    license = 'http://beltoforion.de/article.php?a=muparser&hl=en&p=licence'
    description = 'A library for parsing mathematical expressions'
    source_dir = 'muparser-%s' % source_version

    build_dir = '_build'
    install_dir = '_install'

    def requirements(self):
        if platform.system() == 'Linux':
            self.requires('patchelf/0.10pre-1@vuo/stable')
        elif platform.system() != 'Darwin':
            raise Exception('Unknown platform "%s"' % platform.system())

    def source(self):
        tools.get('https://github.com/beltoforion/muparser/archive/v%s.tar.gz' % self.source_version,
                  sha256='b35fc84e3667d432e3414c8667d5764dfa450ed24a99eeef7ee3f6647d44f301')

        self.run('mv %s/License.txt %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

    def build(self):
        cmake = CMake(self)
        cmake.definitions['BUILD_SHARED_LIBS'] = True
        cmake.definitions['ENABLE_OPENMP'] = False
        cmake.definitions['ENABLE_SAMPLES'] = False
        cmake.definitions['CONAN_DISABLE_CHECK_COMPILER'] = True
        cmake.definitions['CMAKE_BUILD_TYPE'] = 'Release'
        cmake.definitions['CMAKE_C_COMPILER'] = self.deps_cpp_info['llvm'].rootpath + '/bin/clang'
        cmake.definitions['CMAKE_C_FLAGS'] = cmake.definitions['CMAKE_CXX_FLAGS'] = '-Oz'
        cmake.definitions['CMAKE_INSTALL_PREFIX'] = '%s/%s' % (os.getcwd(), self.install_dir)
        if platform.system() == 'Darwin':
            cmake.definitions['CMAKE_OSX_ARCHITECTURES'] = 'x86_64;arm64'
            cmake.definitions['CMAKE_OSX_DEPLOYMENT_TARGET'] = '10.11'
            cmake.definitions['CMAKE_OSX_SYSROOT'] = self.deps_cpp_info['macos-sdk'].rootpath
        cmake.definitions['CMAKE_CXX_COMPILER'] = self.deps_cpp_info['llvm'].rootpath + '/bin/clang++'

        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            cmake.configure(source_dir='../%s' % self.source_dir,
                            build_dir='.')
            cmake.build()
            cmake.install()

        with tools.chdir(self.install_dir):
            if platform.system() == 'Darwin':
                self.run('install_name_tool -id @rpath/libmuparser.dylib lib/libmuparser.dylib')
            elif platform.system() == 'Linux':
                patchelf = self.deps_cpp_info['patchelf'].rootpath + '/bin/patchelf'
                self.run('%s --set-soname libmuparser.so lib/libmuparser.so' % patchelf)

    def package(self):
        if platform.system() == 'Darwin':
            libext = 'dylib'
        elif platform.system() == 'Linux':
            libext = 'so'

        self.copy('*.h', src='%s/include' % self.install_dir, dst='include/muParser')
        self.copy('libmuparser.%s' % libext, src='%s/lib' % self.install_dir, dst='lib')

        self.copy('%s.txt' % self.name, src=self.source_dir, dst='license')

    def package_info(self):
        self.cpp_info.libs = ['muparser']
