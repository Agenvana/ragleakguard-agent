from dotenv import load_dotenv
from agency_swarm import Agency

from auditor_agent import auditor_agent
from rlg_common.config import render_shared_instructions

load_dotenv()


# do not remove this method, it is used in the main.py file to deploy the agency (it has to be a method)
def create_agency(load_threads_callback=None):
    agency = Agency(
        auditor_agent,
        communication_flows=[],
        name="AIDataSecurityAuditor",
        shared_instructions=render_shared_instructions(),
        load_threads_callback=load_threads_callback,
    )

    return agency


if __name__ == "__main__":
    agency = create_agency()

    # run in terminal
    agency.terminal_demo()
