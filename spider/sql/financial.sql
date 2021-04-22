/* Target Server Type : MYSQL */

DROP TABLE IF EXISTS `category`;
CREATE TABLE `category` (
  `id` char(8) NOT NULL COMMENT '网易分类ID',
  `name` varchar(20) NOT NULL COMMENT '证券会分类名称',
  `display` tinyint(3) unsigned DEFAULT NULL COMMENT '显示顺序',
  `parent_id` char(8) DEFAULT NULL COMMENT '父分类ID',
  PRIMARY KEY (`id`),
  KEY `fk_parent` (`parent_id`) USING BTREE,
  CONSTRAINT `category_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `category` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='证监会行业分类';

DROP TABLE IF EXISTS `dividend`;
CREATE TABLE `dividend` (
  `code` char(6) NOT NULL COMMENT '股票代码',
  `year` char(4) NOT NULL COMMENT '分红年度',
  `sg` tinyint(3) unsigned DEFAULT NULL COMMENT '送股',
  `zz` tinyint(3) unsigned DEFAULT NULL COMMENT '转增',
  `px` double DEFAULT NULL COMMENT '派息',
  `ggrq` date NOT NULL COMMENT '公告日期',
  `cqcxr` date DEFAULT NULL COMMENT '除权除息日',
  `fhl` double DEFAULT NULL COMMENT '分红率',
  PRIMARY KEY (`code`,`year`,`ggrq`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='分红派息';

DROP TABLE IF EXISTS `financial`;
CREATE TABLE `financial` (
  `code` char(6) NOT NULL COMMENT '股票代码',
  `date` char(10) NOT NULL COMMENT '财报日',
  `yyhdxjll` double DEFAULT NULL COMMENT '营业活动现金流量',
  `tzhdxjll` double DEFAULT NULL COMMENT '投资活动现金流量',
  `czhdxjll` double DEFAULT NULL COMMENT '筹资活动现金流量',
  `xjyydxj_zzc_bl` double DEFAULT NULL COMMENT '现金与约当现金占总资产比率',
  `yszk_zzc_bl` double DEFAULT NULL COMMENT '应收账款占总资产比率',
  `ch_zzc_bl` double DEFAULT NULL COMMENT '存货占总资产比率',
  `ldzc_zzc_bl` double DEFAULT NULL COMMENT '流动资产占总资产比率',
  `yfzk_zzc_bl` double DEFAULT NULL COMMENT '应付账款占总资产比率',
  `ldfz_zzc_bl` double DEFAULT NULL COMMENT '流动负债占总资产比率',
  `cqfz_zzc_bl` double DEFAULT NULL COMMENT '长期负债占总资产比率',
  `gdqy_zzc_bl` double DEFAULT NULL COMMENT '股东权益占总资产比率',
  `fz_zzc_bl` double DEFAULT NULL COMMENT '负债占资产比率',
  `cqzj_bdc_bl` double DEFAULT NULL COMMENT '长期资金占不动产/厂房及设备比率',
  `ldbl` double DEFAULT NULL COMMENT '流动比率',
  `sdbl` double DEFAULT NULL COMMENT '速动比率',
  `yszkzzl` double DEFAULT NULL COMMENT '应收账款周转率(次)',
  `pjsxrs` double DEFAULT NULL COMMENT '平均收现日数',
  `chzzl` double DEFAULT NULL COMMENT '存货周转率(次)',
  `pjxhrs` double DEFAULT NULL COMMENT '平均销货日数(在库天数)',
  `gdzczzl` double DEFAULT NULL COMMENT '固定资产周转率',
  `zzczzl` double DEFAULT NULL COMMENT '总资产周转率(次)',
  `gdqybcl` double DEFAULT NULL COMMENT '股东权益报酬率(ROE)',
  `zzcbcl` double DEFAULT NULL COMMENT '总资产报酬率(ROA)',
  `yymll` double DEFAULT NULL COMMENT '营业毛利率',
  `yylyl` double DEFAULT NULL COMMENT '营业利益率',
  `jyaqbjl` double DEFAULT NULL COMMENT '经营安全边际率',
  `jll` double DEFAULT NULL COMMENT '净利率',
  `mgyy` double DEFAULT NULL COMMENT '每股盈余',
  `shjl` double DEFAULT NULL COMMENT '税后净利',
  `xjllbl` double DEFAULT NULL COMMENT '现金流量比率',
  `xjllydbl` double DEFAULT NULL COMMENT '现金流量允当比率',
  `xjztzbl` double DEFAULT NULL COMMENT '现金再投资比例',
  PRIMARY KEY (`code`,`date`),
  KEY `date` (`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='财务数据';

DROP TABLE IF EXISTS `stock`;
CREATE TABLE `stock` (
  `code` char(6) NOT NULL COMMENT '股票代码',
  `zwjc` varchar(15) DEFAULT NULL COMMENT '中文简称',
  `zwjc_py` varchar(15) DEFAULT NULL COMMENT '中文简称拼音',
  `gsqc` varchar(50) DEFAULT NULL COMMENT '公司全称',
  `dy` varchar(5) DEFAULT NULL COMMENT '地域',
  `zzxs` varchar(10) DEFAULT NULL COMMENT '组织形式',
  `gswz` varchar(50) DEFAULT NULL COMMENT '公司网站',
  `zyyw` text COMMENT '主营业务',
  `jyfw` text COMMENT '经营范围',
  `clrq` date DEFAULT NULL COMMENT '成立日期',
  `ssrq` date DEFAULT NULL COMMENT '上市日期',
  `sssc` char(2) DEFAULT NULL COMMENT '上市市场',
  `zcxs` varchar(50) DEFAULT NULL COMMENT '主承销商',
  `ssbjr` varchar(50) DEFAULT NULL COMMENT '上市保荐人',
  `kjssws` varchar(50) DEFAULT NULL COMMENT '会计师事务所',
  `sz50` tinyint unsigned DEFAULT NULL COMMENT '是否上证50成份股',
  `hs300` tinyint unsigned DEFAULT NULL COMMENT '是否沪深300成份股',
  `zz500` tinyint unsigned DEFAULT NULL COMMENT '是否中证500成份股',
  `hlzs` tinyint unsigned DEFAULT NULL COMMENT '是否红利指数成份股',
  `kc50` tinyint unsigned DEFAULT NULL COMMENT '是否科创50成份股',
  `category_id` char(8) DEFAULT NULL COMMENT '所属分类',
  PRIMARY KEY (`code`),
  KEY `fl_category` (`category_id`) USING BTREE,
  KEY `index_zwjc_py` (`zwjc_py`),
  KEY `index_zwjc` (`zwjc`),
  CONSTRAINT `stock_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `category` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='股票基本信息';
