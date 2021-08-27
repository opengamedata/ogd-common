# global imports
from datetime import datetime
from pathlib import Path
from unittest import TestCase
from zipfile import ZipFile
# local imports
from interfaces.CSVInterface import CSVInterface

class t_CSVInterface(TestCase):

    TEST_MIN_DATE = datetime(year=2021, month=2, day=1, hour= 0, minute=0, second=0)
    TEST_MAX_DATE = datetime(year=2021, month=2, day=1, hour=10, minute=0, second=0)
    ACTUAL_MIN_DATE = datetime(year=2021, month=2, day=1, hour=0, minute=10, second=43)
    ACTUAL_MAX_DATE = datetime(year=2021, month=2, day=1, hour=19, minute=3, second=48)
    TEST_SESSION_LIST = [21010101103505700,
    21000023305455852, 21010115412037270, 21000023421893364, 21010117132485776, 21010118441143000, 21010111452962156, 21000418535922490, 21010108270998280,
    21010108335648930, 21010108333377450, 21010108373813452, 21000021135436150, 21010108411540216, 21010108533392384, 21010114062116830, 21010109070574484,
    21010109100621570, 21010109103008504, 21010109130844224, 21010109115355664, 21010109145083300, 21010109152191600, 21010109162788190, 21010109191736536,
    21000514255306784, 21010108192073376, 21010109212416910, 21010114213776950, 21010108214687030, 21010114215758960, 21010114222228080, 21010114232170396,
    21010109240287280, 21010114241876744, 21010114245458064, 21010114261541620, 21010114253048532, 21010114265741108, 21010114263157904, 21010109272879730,
    21010114282154010, 21010114284349630, 21010109303262404, 21010114310330024, 21010109373319380, 21010114304097544, 21010114305550812, 21010114273483544,
    21010114311874820, 21010114310385304, 21010114313991984, 21010114302406544, 21010114340627000, 21010108355923896, 21010114355570776, 21010109361301424, 
    21010109394768548, 21010109412282776, 21010109444440976, 21010108454700756, 21010108463346904, 21010109505684850, 21010109515809376, 21010108515962092, 
    21010108523055450, 21010108514887400, 21010108520249980, 21010120530875724, 21010108520176396, 21010108520063136, 21010108515924030, 21010108520216260, 
    21010108520496576, 21010108515805680, 21010108515826950, 21010108531054216, 21010108520381200, 21010108522776510, 21010108523128896, 21010108510137680, 
    21010108520527628, 21010108520591708, 21010108520231696, 21010108520284708, 21010108513963130, 21010108534011280, 21010109552105692, 21010108552079030, 
    21010108563254416, 21000608395670090, 21010108594418964, 21010108595369784, 21010121021685868, 21010110034422570, 21010110051902336, 21010110044057348, 
    21010110043801330, 21010115044111776, 21010109050773624, 21010109045700670, 21010109053406000, 21010110052107690, 21010110040968370, 21010110052024510, 
    21010110053700420, 21010110060351344, 21010110062372876, 21010109065544680, 21010110064760316, 21010110063051468, 21010110064508840, 21010110071721680, 
    21010109053635990, 21010110071217080, 21010110064695572, 21010109073697184, 21010110084290984, 21010110082786948, 21010110091482064, 21010110091323436, 
    21010110091464190, 21010110091811350, 21010110092578364, 21010109093542810, 21010110094887136, 21010110094739388, 21010109102896016, 21010110100581600, 
    21010110051914388, 21010110111006932, 21010110110149930, 21010110110690980, 21010109012401404, 21010110114848510, 21010110113818108, 21010110143880616, 
    21010109105308828, 21010110121689268, 21010110125668348, 21010110124297450, 21010109131878476, 21010110104495732, 21010110113517140, 21010110135860216, 
    21010110144950256, 21010109145276210, 21010110143762456, 21010110145215652, 21010110152130724, 21010110151528130, 21010110151914732, 21010110153046630, 
    21010109155212890, 21010109161978864, 21010110115808816, 21010109163573370, 21010110171216744, 21010110172062976, 21010110173514250, 21010110173778884, 
    21010110175976532, 21010110181075676, 21010110180555024, 21010110175087640, 21010110182300508, 21010110185510756, 21010110185253410, 21010110194680200, 
    21010110201932304, 21010110202990132, 21010110213957788, 21010110214975844, 21010110213663224, 21010110220378332, 21010109221272976, 21010110222568980, 
    21010110215384170, 21010110230628860, 21010110232249970, 21010110221183496, 21010110242798696, 21010110251605100, 21010110302465504, 21010110305838930, 
    21010109325002936, 21010109350238904, 21010109364859584, 21010109382563144, 21010110404499904, 21010110415475570, 21010110444562960, 21010110435948428, 
    21010110445360756, 21010115452597720, 21010110454547760, 21010110461112812, 21010109463595880, 21010110461944116, 21010109462908150, 21010110471519480, 
    21010110491046644, 21010109492007536, 21010110495384436, 21010106503171890, 21010110571666436, 21010109570078116, 21010109565541068, 21010115580704280, 
    21010109572227836, 21010109583032190, 21010109583716930, 21010109585054004, 21010109584882670, 21010110000842588, 21010109593906220, 21010109593501640, 
    21010109593889650]
    zipped_file = ZipFile(Path("tests/t_interfaces/BACTERIA_20210201_to_20210202_5c61198_events.zip"))

    def RunAll(self):
        self.test_IDsFromDates()
        self.test_DatesFromIDs()
        print("Ran all t_CSVInterface tests.")

    def test_IDsFromDates(self):
        with self.zipped_file.open(self.zipped_file.namelist()[0]) as f:
            CSVI = CSVInterface(game_id='BACTERIA', filepath_or_buffer=f, delim='\t')
            if CSVI.Open():
                result_session_list = CSVI.IDsFromDates(self.TEST_MIN_DATE, self.TEST_MAX_DATE)
                self.assertNotEqual(result_session_list, None)
                if result_session_list is not None:
                    diff = set(result_session_list).symmetric_difference(set(self.TEST_SESSION_LIST))
                    self.assertTrue(len(diff) > 0, f"Date range for missed items: {CSVI.DatesFromIDs(list(diff))}")
            else:
                raise FileNotFoundError('Could not open the test data TSV!')

    def test_DatesFromIDs(self):
        with self.zipped_file.open(self.zipped_file.namelist()[0]) as f:
            CSVI = CSVInterface(game_id='BACTERIA', filepath_or_buffer=f, delim='\t')
            if CSVI.Open():
                dates = CSVI.DatesFromIDs(self.TEST_SESSION_LIST)
                self.assertEqual(dates['min'], self.ACTUAL_MIN_DATE)
                self.assertEqual(dates['max'], self.ACTUAL_MAX_DATE)
            else:
                raise FileNotFoundError('Could not open the test data TSV!')