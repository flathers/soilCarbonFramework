Here are steps to execute the Random Forest Regression model using
a virtual machine on the Amazon EC2 service:

You should have a keypair generated for logging into an EC2 instance
and use that existing keypair in step 6.

If you wish to use Amazon S3 for storage, you should have an S3 bucket
configured and use the details of that bucket to configure s3cmd.

From the EC2 dashboard:
  1. Launch Instance
  2. Choose Ubuntu Server 14.04 LTS (HVM), SSD Volume Type - ami-8f78c2f7
  3. Instance Type: i3.8xlarge
  4. Review and Launch
  5. Launch
  6. Choose existing keypair
  7. View instances
  8. Find the public IP address

Connect to the EC2 instance using the public IP address and an SSH client.

Below are the commands to be entered into the console once logged in:

sudo su

# mount temp storage
mkdir /workspace
mkdir /workspace/outputs
mkfs.ext4 /dev/nvme0n1
mount -t ext4 /dev/nvme0n1 /workspace
chown -R ubuntu /workspace

# install R
sh -c 'echo "deb http://cran.rstudio.com/bin/linux/ubuntu trusty/" >> /etc/apt/sources.list'
gpg --keyserver keyserver.ubuntu.com --recv-key E084DAB9
gpg -a --export E084DAB9 | sudo apt-key add -
apt-get update
apt-get -y install r-base python-dateutil
exit

# connect to s3
wget https://github.com/s3tools/s3cmd/archive/master.zip
unzip master.zip
cd s3cmd-master/

# configure s3cmd
# These configuration settings will depend upon your S3 bucket details
./s3cmd --configure

./s3cmd ls s3://mybucket

# get the data from s3
./s3cmd get s3://mybucket/samples.csv /workspace/samples.csv
./s3cmd get s3://mybucket/grid07252017.zip /workspace/grid07252017.zip
cd /workspace
unzip grid07252017.zip

# do the analysis
echo "TMP = '/workspace'" >> .Renviron
screen
R

# now, follow the steps in the 'scorpan.R' file

# after you're finished in R, send the output back to s3
zip output.zip msoc.asc vsoc.asc rawdata.csv
cd s3cmd-master
./s3cmd put /workspace/output.zip s3://mybucket/output.zip
