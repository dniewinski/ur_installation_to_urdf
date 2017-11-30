# ur_installation_to_urdf

This is a script/ROS package that will take the installation file from a UR controller and update the URDF in ROS to match.  Settings include:
- Joint Position Limits
- Joint Speed Limits
- Joint Force Limits

Tested with UR PolyScope 3.3.4.310 and 3.4.0.265

## Getting Started

Save a .installation file from the robot and copy it to your local machine.  
update_urdf_from_installation.py [urdf_location] [installation_location]

### Prerequisites

pip install xmltodict
