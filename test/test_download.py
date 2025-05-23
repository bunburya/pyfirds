import os
import logging
import random
from datetime import datetime, date

from lxml import etree

from pyfirds.download import EsmaFirdsSearcher, FileType, FcaFirdsSearcher

from test.common import get_test_run_dir

RUN_DIR = get_test_run_dir(__name__)

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

esma = EsmaFirdsSearcher()
fca = FcaFirdsSearcher()

esma_search_params_to_checksums = {
    (
        datetime(2023, 3, 23),
        datetime(2023, 4, 2, 23, 59, 59),
        '*'
    ): [
        '790a4e49f11371b56cddbf0661671e36',
        '9b36cd05a2f76a1ee993f32845bb6961',
        '2092255a18d9c7839d7d3cb9dcff07fc',
        'ab7f67bb6e5d3f93d81e48c7042034b2',
        '0b082470105505392c502ff290eefaba',
        '15985c17b0632f00012ffdf6ca406ab4',
        '1f4d15c07507603743d40125f4002185',
        '6dd09cc19390cc49e8f3936d2c4316c1',
        '12ca9efc3dbcc64fb4b7c30fa882a34e',
        '9a412ffa2e0d45351a634f489f585f18',
        'c99af7dc7219feb8bdbbb5d10ae82f32',
        'c3176825ad4d2457c9d6f3f1f03e5c34',
        'daaf4ed2439c24a773cb6439e78a6f95',
        '16c535499dca62480962095e4739e923',
        '7fba47eb692374b231c2b118949fed5a',
        '64516f106751a7cc4d9307d1c17385a4',
        'fd60be2eda5a9fc214d3b7e186e5fd8e',
        'c335a9fc8b06d8268463fda314bbd23f',
        '2940c692a285aae4dcbe073976e0e410',
        'afbeb911c19b54eb8e97237f9cc3765d',
        '43c3cafc426f9e1ba04baf31d18be6cc',
        '790886ef0c4d2f070ed63aa0c1af3d91',
        '20e2c0a7e5938dfc1d55fd675c86effc',
        '56e19666631824e9f0a3eb92b262036d',
        '426317d3cde3f357027f4fbd8f8a94a7',
        'c09bc53a6674a94309fe89dce61cd6f4',
        'c0910951605ed0774ef4ff257134a9dc',
        '2b5edad1585b187a6e631314fe36cacf',
        '4c0065f73c7a4deb8b6922facbcadad4',
        '3d0c135377904a16a1b06b1f6642dc44',
        '71944fcdbd4cfd343be424222decad3f',
        '2addf536c7f4b532fa578f441cdbb748',
        '7f227b8dfde9d0df32cb86b991563736',
        '8dd80c6ca88d3beeb84f10f8d53772a6',
        '337eca275ffacbfe6ee7e06c2e270963',
        '4821679ffb5f7c2c7ed457bbe94ed442',
        '899003446f07ede1240edebc2097cefb',
        'c1c0a6a983fcf5a741aae312e09b53ed',
        '1e4d9cb4f5ab77181e5d1745565e885e',
        '48a114c5362a03eee489b6221b588969',
        'e4df94da9041da5db97f64ea54ad7df1',
        '8e5a2b5cae535b0e9501831488f95741',
        '6a38d88c4f7c4e5b6540558978a5a1d2',
        '2779939aa1e26d727a962b772de8c621',
        'dfaffa77c0c71da7de278720223d6cc1',
        '4088a2d14fc52946c81cac9d54ab6465',
        '7b725d75fbe6f94a5b87f762ff7da866',
        '326d00f65a2534b32eb44d3132e4652c',
        'bf78481681fc93ea336d8d4986e73ee9',
        'f4953154660d92771349fd023c3e573b',
        'c6864f99d27606b7b1f63d16a7cf44f4',
        'b581da71435ddc56ded418d734111974',
        '147fd63b7d3c520114cb782b26f97d3c',
        '94c6323fbd966910ffb0ccea3e025ecd',
        'aade951b5a2a52b80a27d89258fa484d',
        '4ac098169d6f3e6655c665cf5c2e2885',
        '17360bfb1c8750b458eb4445b84cc828',
        'ea432d91ec919f057c70d60a5c461bd1',
        'c15b6f5862b3ca6092549914b259ecca',
        '05389294624ffe9afcf15c4026232a8f',
        'f63cf39ecbde8dcbe9725ee7a94f2584'
    ],
    (
        datetime(2021, 2, 1),
        datetime(2021, 3, 14, 23, 59, 59),
        '*'
    ): [
        '0bd1f7f0acc84bb11bf4b84cbd2044d7',
        '57eb3f88e1231290b8c6a91715bfeac8',
        '4fcb02e1dc1a2fca81fb2d73cda47116',
        'c16c833eead8f0b5df68fcdabbce328d',
        '753ba8c4504fc34bbf580c5c618f1abc',
        'c81aa753cfb8e97902e203fe6798d4c7',
        '7dc3f0cbd9e64df708e3a8449618b025',
        'e4db6fa4c68002e7319357073bc55ba4',
        'a9ca5b165dd5ee785de6a30fce94d5fe',
        '0c4217395ce952ebd897e8db656803f5',
        '1636c88937ffc6be510f689d789c1a8b',
        'dc2b20d50e4a48d0670f3a33fc994e3b',
        '033dc33bbef3bda2936d7f984b825b1a',
        'a08a3ce1bbc907d9cc4418b4c3cbb327',
        '33aa134a6a59feaf272340befeac40e4',
        '9775a10c322b3511e04447eea7709401',
        '60998cfd5074af1439aac9ac7eac11df',
        'b966aae23c1fa7e78e3f0727a34178b3',
        'a5aef3a8552b4be5a3e7c97d5bcfa90e',
        '6a0944d34c4ea20f945a2d10c681e6f0',
        '69643da121bb4de123172c09457f9f51',
        'be2e66452629fd29fba262fa4d5cbe95',
        '3c561f62b67b4d6cabd8998c7522b7c6',
        '0f008e3fa3e2480a79406270d70235b3',
        '1e1267ed18d0e11666a03bb23fa12446',
        'a0dd821b0049502916ecd2308ec0eb9b',
        'c8dc59650b3365eded6b2ee4929d518d',
        'a7170c4ee08f669340d39a23f6766c7e',
        '13c56fc7f86b8a5b4b5e8d1bdc02b917',
        '41edd99ba4ee198c13da3919ede63875',
        '8a300c97a8b4c40ab17d036bc75d022c',
        '47da85e572f5c891c4ca9e722afbd083',
        '9caed328cb6ce0c928b77a6a3e7f59cb',
        '78fa7c36e600e8e1f9353c516c58f7e0',
        '6e2681b63e7ff9e9c0e7033f605854ad',
        '44adc236bc75542fed8d8db453fa6f7c',
        'bc19a406f067bedff160e48ffe392d36',
        'af61585dea851e914ef998f46efca488',
        '74911a52e0239312e8f2b92523cbad38',
        '8a5daec8959615acb08e3b9b8ea35c6a',
        '3dfbc9a517be9677bd8917053be96184',
        'b07b89a6fb079357c906c02b758b3199',
        'd71561e438e44cb77d7985e5325d66c6',
        'af5d9381ae7585a4ab509291da0673d3',
        'db2579b23afe037e8f877c3e196ae634',
        '83239c1f7989b932f3c8a3ce41641f7c',
        'e35bbf7305d0f0ca71cd6f59d58dec83',
        'f007150ba64d840b70180e392a30f5dc',
        '191c3f926b1b602894e7c7be04f5111b',
        '3b788f7b1a27f8e1066810f5c3b31a38',
        '3be0e5d428f9d331201b28fd3380bf2a',
        '179d2c33717d3783b2048b76d8573d3c',
        'be35c43549f1a2cff4006eb076642d24',
        'dac52e06898a04aab6c2f368fb57db9d',
        '9a2e7833dd6af67c2e347d87e0ff5226',
        '64b9c6afe342811f32c24e80a5b02240',
        '5f5047919f46762907ca393b73cba654',
        '70d860fe2651cb4db1cee8e9029e4d2d',
        '6eec8eae89e7b415ef5164e34ee53f5a',
        'df6b269a5484481c3fb51680081e350a',
        'e72d25d9ea7a582c413888452558b4c2',
        '44feaf79a895b3bef18aedbc0f01bbbc',
        '87b3526e789a4388c4dc1afca3fea965',
        'b120e32285539e1c362b77dd571f3f25',
        'e4fa8b659b6c192d424d40c740c47804',
        '4a4f9c596fc9b5a9e5688a0b92a63f6f',
        '976ca4fe639fc3e98ec70e4971850753',
        '5e8ef53e138c503333ee430de249db4f',
        '2fda7614ce0e485aa04490a0dfde509f',
        'fda6dc64af180f023d6bc335b7f31e5f',
        '2ff1c1f49cab382f7b548a8354d40495',
        'd7093e2bf824583afd109461d3c575d7',
        '96311ae113d2051377c7f8b0d66a4a4f',
        '689d51ef73c2439d2294fa9289d7f448',
        '3163c24f70587ba228f7748d44b6ad38',
        '3eced8a62de5ebb9c2aa4bfbbed7cdd8',
        '0f2225c91963618f7977810cb11a8884',
        'f114f2e5432a4bf6997b3d0f2852ec95',
        '7acef3fc3904010dce59b2e161c41285',
        '158ee3c08a2287b18aa4dad7b6e436b2',
        'e4a7c85eb4fb8e9a8dbcee8c37ca1437',
        'b2ac2f5582243be8fee33fdce89e1d3d',
        '32afd9a32cdf32d94c23706502d8a4a4',
        '60c89d845745f114cb5634dea3a6a8cc',
        'daf3beaba930a16286cda61bc9f617cc',
        '46835864869631def7afec87c8d97313',
        'ed2116ae7ac4ec1877bb0b36ce404947',
        '5df96fac1a7b14b981f76a41ec671960',
        '008018ae8e0b21fc24f08932dc73a92c',
        'ed38ef561b56d1655f289c68899efb73',
        '355ea24850870b372248d6443ef2d34d',
        '9bdd710855d9d4267a0c1016cef15940',
        '7ba61e8b14d97461eaa0c81ce929c02e',
        '013e0d174f8275eb76c710dedba56236',
        '3b04ce955fc317463e92ef94e965d4c3',
        '0d02527fb25254f24a718b53dab4d568',
        'dcbd2ed6c4fe924f522a8fe30edfc105',
        'd429d8b8c55e578a125b5f73260fa9fe',
        'bddb9fa6cf839a9b6cd235f875031a8e',
        '2503c1ce789031d173f1bb3d637fb36f',
        'a2918a6440bf0de7d97502b4b2b88157',
        '80cbaa6339e400a08920f7ae737a5447',
        '409d436c36535f8823ae4fe6d30afb59',
        '44d78f6afef13fdc328ad5ca81b85234',
        'a388c994e101c7606e1b4f84a3fe9c3b',
        '30861288586e34a29921655082e97b5d',
        '57e9be2b917753207bc730b8f5e49f3c',
        '8bf867cc58c1bd9411c858c9adcee855',
        'd8b10198ca51e8d3b2a39291fb0c47f9',
        '7877976993be5e0452b2cc8c7f66d962',
        '28776a2b3184bf7db92b7bba53f1aee1',
        'e041bccd28dfeeddf6bb13b5f2d197e1',
        'c2cbaa35ed30545fe548468f24f713ce',
        '57cd5513192ad096ff10935909ddd703',
        'e7e1ec6dac00d3f29529c39b14940670',
        '8451955f6ab3d7304e6ab0481af838ea',
        'c7adf495d16b84d703d93bff66f52a1d',
        'd339c201fa1363e87e749b8d0c6562e7',
        'cfb170e4fc7a8b1ba8578953dc8cb470',
        'a4d399fd5c57e4937bc4f80b2275907c',
        '95b67f08a43fb4f0fb3834cde03319ca',
        '8748bdf345a591e8295d2ed4d84cfd25',
        'b7a744468ba2c30431ffae74020d29d5',
        '0a553b85bcb0917688943944ea7363d6',
        'f33b858f734eabac7cbb7a3b2dd67945',
        'ff525db3d34cb59020c492b75e0d8a8b',
        '87a836e0b2e51ad202bdf8617b64a543',
        '95af56b94f0d63de89d0fab9d0d403a0',
        '396271b2618597bb9ed59186f1b1a852',
        '4c270ccb1898e2ad13bb6d944f1cb405',
        '1b51e31d456fbf439b9bc75608f222cb',
        '0738d3be9823abdba2914000b5e3a6f1',
        'e521635c6278506c04008729e716f991',
        '06f9c1b41d05640d3f302a52dbf1153f',
        '6bd9f7a9f0522016b98107a06dfcf879',
        '45f546673d2591c8cb7d79726c0a02f9',
        '1016cc6ab5b60785f2f1174ea62277eb',
        '4ba8685ff3724795f12135b747ec8b80',
        '6c1c9fa966429a52da0d3e8b7a72c649',
        'a5834041c949ef8d4c2e1eb5ba9fc863',
        '8ad969cc33c097ec28dc1d552aaade41',
        'a73020523ab7a0e0cb6f48f66c2a5a2c',
        '78bfb7099f179885b0567d2673e8191b',
        'fc20c0a948ea6e4695c43b94e6e62d0e',
        '4c76a47dc21c07cee22267b4982f49f2',
        '52f9f9a03e68e39e6ade76a38a2d6b76',
        'ce4754c8508ae2c2bae2f73406d06878',
        'd3042e83b1ac62b87f35bf52e6c083bf',
        '86beea38ab32c4a27a8a539a2fd8d111',
        '2a56807365f8c62c7f405d627206f715',
        '3178b44b9fb4a5e52297d97afc0a7ed2',
        '5e7a4e84231043e0a00f0063c5206c23',
        'a612018060facc0fc78c8fcfe3180711',
        '818558579474997eef9456a1007cafdf',
        'bcccc05ea5668a24d4adec6af107d9d1',
        'f895cc62fb46001b0af37b633b498cc8',
        '3a5e6aa1602aea0906e835ab0ee39320',
        '5d6e2c266dcd40a83359cc062a924ee7',
        'a1fd99a6840e852fe0b2a664d4c575d6',
        '8670e1d49672f4375f46475135c1db6e',
        'efdb7659041fda422aedcb0ffba533c7',
        'a39bac7839a22a0f17c7ad8015e3ae53',
        'a1a88cfb765e6c766a5163f7dd117954',
        'ea663d80ec09bab5484a758234ab1e6b',
        'e3b0dbefb741ce2768f20cc3ea60c4d1',
        'f530c9d3149dce118a1d4d4caffd1c42',
        'c5eb30ad6dd54ac4bf1bffed5fa2425e',
        'f2a137db0b9d56ed142880fe29d40ba3',
        'e74f98699827072199e690c27964c77e',
        '949d52092ecb85ded366dbc40355f9a1',
        'd510deccbf49b02e2d4110ff12859aad',
        '2118a9121542cb1df19742c00e6c1193',
        '41bb9a632f259bd37220deaa786027f2',
        '37416b4afa3d35d76a51c12888bb1fb1',
        'f8a62dd6a7d630293dfd21e7f2675a7c',
        '44dd07da00ea42bb4bda2567bac431fc',
        '9ab56906c7422fea0246e135cedfbc37',
        '86c87d43300d429ede0aeb7604fccaab',
        '1f5eea14757d980dfe154855294d426d',
        '2987f7ab00893d416bd0b2365f6fde8e',
        'c0e8435ec6b8be4787fb96bd6d756786',
        'f153a89be9bc5ecbbb5d22d2d658e5e0',
        '7b2bd97d3a63284b73d406032d7f9c59',
        '9eb9ed93c2773b17f09f782be551c180',
        '60b5b861e780ac8643bf448274faa419',
        '92bb6fce9247d5b7bfffc989de1e248b'
    ],
    (
        datetime(2022, 8, 12),
        datetime(2022, 8, 21, 23, 59, 59),
        'FULINS'
    ): [
        '20c8e344614c17dafe5abfc25bb4708c',
        '387e117906b619cba557284833095e06',
        '210b0527515cf60022a6a60eac876f09',
        '526c5d276320f799d81ca2c65bdcad88',
        '13e3eeb5b1eb4dfb70f4e9fd2a138ba8',
        '1fe4e5a4416391e35e4556a3e562b0cd',
        'fdcb4a7f72e3e0b7fa7a27879839329b',
        '068ad995589df49850c5279cd262d062',
        'ba1c1b860514976b10a9fe807a475ddc',
        'bd71785d5296262b3e6596f70a1f2d57',
        '6a453c77c5f6b20134b2e6b08d483fda',
        '5d45bbe1cce534f8cbdfcb78ee90a4e6',
        '851327335fbb25ab700af9c90bb3b293',
        '79cd38bec77ceba1ee3724451d9f467f',
        '6e756adb31a866439f2bc6ea7016a531',
        'ff0272338f4f6dd6f569990b569f4766',
        '354938968d0b3543810c497093e0fa21',
        'e1bf40fe87f402e0706f6aab035ff019',
        'aa0a2a712f2ede5b2af7a50f49fa631a',
        'b8bcb2f5ece435143eb7038ba2dca236',
        'f78b241f13577574d9b49f2f9456b76d',
        '37e8e97bf10e627e8923c7183ef2eaf0',
        '0399fcc5ca1cf8b8eaebd11d128aa2aa',
        '2d1d8c4d54b0312b508b3aede53f8002',
        '57ac3fb2977025775b819fed2ea53de2',
        'f9cf338603163a17357085665bbadc65',
        'bb51930c052b42becbe4b7c5b7551bdd',
        '45e2ea7aafeffb394569e8753f82947c',
        'a2921b1ecb5bb8935b375a6f81ff7055',
        'ff868a3871fd3279ef1f6bf9d689f9a2',
        '6d8ea7ce0e367aa80942d37218c6d636',
        'ecc2e967296b4187b0598c874753bd12',
        'a33f7f01e4d8cd2c23e9568e4b9fd47a',
        'fcbc69bf8c2e06e08d21fa06a6ec63aa',
        'bc77ddfcc3f808a7efdde484ce9f57e5',
        '7618c58ac46eb9a02dacd5514866ae44',
        'ae53bbd89be356fcd235887af0a27326',
        '56c7025a3b1fff74f0621c470834baa6',
        '6e61721ff84e0f753b858f6124099db2',
        '8972932bad81ac52907581b0026599a4',
        'b9c849fed669114a4fe8e08e4cb7a307',
        'c76d750b24f036e88dc62e1b262e68d3',
        '4bcd13fa19d87e8ac2ac87e0adeb6285',
        'c9c3f0d29f43248e38102c96719cb0e3'
    ],
    (
        datetime(2022, 8, 12),
        datetime(2022, 8, 21, 23, 59, 59),
        'DLTINS'
    ): [
        'a9d7fc6576025e912e8df7502cf04ffd',
        'd67527173c41d638a75ef0d833d28588',
        '8ffff51dc7bffd64a97ded4c67d3a2b6',
        '02deaef58e7f8d6acff9caccc58a23c1',
        'b6cc754fe342fea9d551d9f02633ddfc',
        '1ccc7eb49c667019dfb6df2398b3e861',
        '5119094e3ebbad59efe73ac73b995dfa',
        'd993dd028f6d1a2d83a41f5235fbfa00',
        'de225e738d543c3430805cd4a87db039',
        '16f336cfef8b93ca580b6a8eb9a9090b',
        'e423bce1880c35a1387f89979bb0419e',
        '6708759a819f93202f5765d389cdef4a',
        '4c6dc389ce84e28c1e5859b6fbf33ee1',
        '2db98d0edff3fd205797630bbe420b85',
        '5491936296df74cd32289975709bfbd2',
        '52949059e5c8cf2103f7eee9e7f60348'
    ],
    (
        datetime(2022, 8, 12),
        datetime(2022, 8, 21, 23, 59, 59),
        'FULCAN'
    ): [
        '2b2a61b378e730de7fa6daad946f3a6e',
        'd13e811b9daf7f7d2064f787acdf2bd0',
        'aca6c2b0823ae1be2ff460dc85d45e0f',
        '2c83be3b69ef70dc7b25d9d48dbfdcfa'
    ],
    (
        datetime(2023, 1, 1),
        datetime(2023, 1, 1, 23, 59, 59),
        'FULCAN'
    ): []
}

fca_search_params_to_hits = {
    (date(2024, 10, 15), date(2024, 12, 31), FileType.FULINS): 339
}

def test_01_search_esma():
    for from_time, to_time, q in esma_search_params_to_checksums:
        results = esma.search(from_time, to_time, q)
        checks = esma_search_params_to_checksums[(from_time, to_time, q)]
        assert len(results) == len(checks)
        for r, c in zip(results, checks):
            assert r.checksum == c
            if q != '*':
                assert r.file_type == q

def test_02_search_fca():
    for from_date, to_date, ft in fca_search_params_to_hits:
        results = fca.search(from_date, to_date, ft)
        assert len(results) == fca_search_params_to_hits[(from_date, to_date, ft)]

def test_03_download_esma():
    for from_time, to_time, q in esma_search_params_to_checksums:
        results = esma.search(from_time, to_time, q)
        for r in random.choices(results, k=min(10, len(results))):
            xml_fpath = r.download_xml(RUN_DIR, overwrite=True, verify=True, delete_zip=True)
            logger.debug(f'Testing parsing of XML file {xml_fpath}.')
            etree.parse(xml_fpath)
            os.remove(xml_fpath)

def test_04_download_fca():
    for from_time, to_time, ft in fca_search_params_to_hits:
        results = fca.search(from_time, to_time, ft)
        for r in random.choices(results, k=min(10, len(results))):
            xml_fpath = r.download_xml(RUN_DIR, overwrite=True, verify=False, delete_zip=True)
            logger.debug(f'Testing parsing of XML file {xml_fpath}.')
            etree.parse(xml_fpath)
            os.remove(xml_fpath)

