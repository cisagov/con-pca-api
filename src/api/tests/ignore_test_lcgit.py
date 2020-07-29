"""
A test harness to implment and test the lcgit library.

Includes method to generate targets in the same strucutre expected in a new subscription.
Implmentation of a method to seperate a list of targets into n deception level groups included.
"""

# Third-Party Libraries
# Local
from faker import Faker
from lcgit import lcg

target_count = 6
max_deception_level = 3  # Between 1-3, need to modify decp_key and decp_list if larger numbers are required


decp_key = {"1": "low", "2": "moderate", "3": "high"}
decp_list = ["low", "moderate", "high"]

faker = Faker()


def generate_target_array():
    """Generate a list of fake targets."""
    target_list = []
    for i in range(target_count):
        new_target = {
            "id": i,  # Variable for testing
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "postition": "Target's Position",
        }
        new_target[
            "email"
        ] = f"{new_target['last_name']}.{new_target['first_name']}@testing.com"
        new_target.update(level={"low": False, "moderate": False, "high": False})
        target_list.append(new_target)
    return target_list


def seperate_targets_to_campaigns(target_list: list, max_deception: int = 3):
    """Given a list of targets, seperate them into n groups based on the max deception level."""
    # Assign a random order to the target list using the lcgit library
    target_lcg = lcg(target_list)

    # create a return array and populate n amount of empty arrays, one for each deception level
    campaign_groups = []
    for i in range(max_deception):
        campaign_groups.append([])

    # Modify each target to identify which deception level they have participated in
    for index, target in enumerate(target_lcg):
        decep_lvl = index % max_deception
        # If all all levels have been received, set all to false for the following year and assign the current random decep level for the final cycle
        if allLevelsTrue(target["level"]):
            target["level"] = {"low": False, "moderate": False, "high": False}
        # Assign current deception level if the target has not previously had it assigned
        elif not target["level"][num_to_decep_lvl(decep_lvl)]:
            target["level"][num_to_decep_lvl(decep_lvl)] = True
        # Count up through deception levels untill one the target has not been assigned is found and assign it. Reseting to 0 if above max deception
        else:
            for i in range(max_deception):
                decep_lvl += 1
                if decep_lvl >= max_deception:
                    decep_lvl = 0
                if not target["level"][num_to_decep_lvl(decep_lvl)]:
                    target["level"][num_to_decep_lvl(decep_lvl)] = True
                    break
        # Assign to a campaign group based on what deception level was given to the target
        campaign_groups[decep_lvl].append(target)
    return campaign_groups


# Helper Methods
def num_to_decep_lvl(num):
    """Convert index to decpeption value (low, moderate, high)."""
    return decp_list[num]


def allLevelsTrue(levels: list):
    """Determine if a target has been seen one of every deception level."""
    for key, value in levels.items():
        if value is False:
            return False
    return True


# Unit Tests
def test_all_users_in_group():
    """Test if the individual groups contains the same amount of targets."""
    target_array = generate_target_array()
    campaign_targets = seperate_targets_to_campaigns(target_array)
    all_campaign_targets = []
    for i in campaign_targets:
        all_campaign_targets += i

    # assert len(target_array) == len(all_campaign_targets)


# Testing method to ouput results to console for debugging

# def test_output():
#     target_list = generate_target_array()
#     campaign_targets = seperate_targets_to_campaigns(target_list)
#     for i in campaign_targets:
#         print(len(i))
#     print("-----------")
#     campaign_targets = seperate_targets_to_campaigns(target_list)
#     for i in campaign_targets:
#         print(len(i))
#     print("-----------")
#     campaign_targets = seperate_targets_to_campaigns(target_list)
#     for i in campaign_targets:
#         print(len(i))
#     print("-----------")
#     campaign_targets = seperate_targets_to_campaigns(target_list)
#     for i in campaign_targets:
#         print(len(i))
#     print("-----------")
#     assert 1 == 1
