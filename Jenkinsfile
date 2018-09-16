pipline {
    agent none
    stages {
        stage('Test') {
	    agent {
	        docker {
		    image 'qnib/pytest'
		}
	    }
	    steps {
	        sh 'python3 -m unittest tests.unit_tests'
	    }
	}
    }
}