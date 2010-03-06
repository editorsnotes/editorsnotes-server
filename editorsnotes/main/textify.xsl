<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:template match="div">
    <xsl:copy>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
    <xsl:text> </xsl:text>
  </xsl:template>

  <xsl:template match="p">
    <xsl:copy>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
    <xsl:text> </xsl:text>
  </xsl:template>

  <xsl:template match="a"> 
    <xsl:apply-templates/>
  </xsl:template>

</xsl:stylesheet>
