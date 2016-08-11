DROP TABLE IF EXISTS portLUT;

CREATE TABLE portLUT
(port              INT UNSIGNED NOT NULL
,active            BOOL NOT NULL DEFAULT TRUE
,tcp               BOOL NOT NULL DEFAULT TRUE
,udp               BOOL NOT NULL DEFAULT TRUE
,name              VARCHAR(10) NOT NULL DEFAULT ""
,description       VARCHAR(255) NOT NULL DEFAULT ""
,CONSTRAINT PKportLUT PRIMARY KEY (port)
);

CREATE TABLE IF NOT EXISTS portAliasLUT
(port              INT UNSIGNED NOT NULL
,name              VARCHAR(10) NOT NULL DEFAULT ""
,description       VARCHAR(255) NOT NULL DEFAULT ""
,CONSTRAINT PKportAliasLUT PRIMARY KEY (port)
);