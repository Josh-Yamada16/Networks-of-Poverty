from basicsimSetup import BasicSimSetup
from centralInstitutionNode import CentralInstitutionNode as CI


def main():
    no_central = BasicSimSetup()
    add_central = BasicSimSetup()
    no_central.setup_basic_simulation(central_institution_toggle=False)
    add_central.setup_basic_simulation(central_institution_toggle=True)

if __name__ == "__main__":
    main()