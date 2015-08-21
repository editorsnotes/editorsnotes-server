<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:template match="div | p | h1 | h2 | h3 | h4 | h5 | h6 ">
    <xsl:copy>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
    <xsl:text> </xsl:text>
  </xsl:template>

  <xsl:template match="a | span | strong | em"> 
    <xsl:copy>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
