# ur_installation_to_urdf

This is a script/ROS package that will take the installation file from a UR controller and update the URDF in ROS to match.  Settings include:
- Joint Position Limits
- Joint Speed Limits
- Joint Force Limits

## Getting Started

update_urdf_from_installation.py [urdf_location] [installation_location]

### Prerequisites

pip install xmltodict
