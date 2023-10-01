# TODO

- [X] Finish parsing XML into dataclasses
  - [X] Add testing
  - [X] iterparse version
  - [X] parsing delta files
- [ ] Add support for downloading from FCA
  - [ ] Add testing for downloading from FCA
  - [ ] Add testing for parsing FCA data into dataclasses
- [ ] Add database support with SqlAlchemy
  - [X] Schema for reference data
  - [ ] DAO/Repo class for interacting with DB
    - [ ] Add instrument
    - [ ] Replace instrument
    - [ ] Delete instrument
    - [ ] Search instruments
    - [ ] Pandas support
  - [ ] Add testing
- [ ] Consider adding dataclasses for:
  - [ ] CFI
  - [ ] ISIN
  - [ ] LEI
  - [ ] FISN
  - [ ] MIC


## XML parsing tests

- [X] Try parse everything without error
- [X] Ensure resulting dataclasses have correct property types
